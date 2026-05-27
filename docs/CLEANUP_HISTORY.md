# Plan de limpieza del historial (BFG / git filter-repo)

Objetivo: eliminar archivos binarios grandes (imágenes, capturas) del historial Git para reducir el tamaño del repositorio.

Archivos detectados (ejemplos):
- `frontend/public/login-bg.png`
- `frontend/src/assets/login-bg.png`
- `backend/error_screenshot.png`
- `ui_steps/screenshots/*`
- `nexacorp.png`

Pasos propuestos (NO DESTRUCTIVOS hasta aprobación):

1. Crear rama de planificación desde `develop`: `feature/repo-cleanup-plan`.
2. Añadir documentación y scripts de análisis (este PR).
3. Ejecutar análisis local para confirmar ahorro esperado:

```bash
git clone --mirror <repo-url> repo.git
cd repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git verify-pack -v objects/pack/pack-*.idx | sort -k3 -n | tail -n 50
```

O alternativamente usar `git rev-list` para listar objetos grandes:

```bash
git rev-list --objects --all \
  | sed -n 's/^[^ ]* //p' \
  | sort | uniq -c | sort -rn | head -n 50
```

4. Usar `bfg-repo-cleaner` o `git filter-repo` para eliminar los paths aprobados. Ejemplo con BFG:

```bash
java -jar bfg.jar --delete-files "frontend/public/login-bg.png,frontend/src/assets/login-bg.png,*.png" repo.git
cd repo.git
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

5. Verificar el repositorio resultante localmente y ejecutar tests/build.
6. Forzar push de la mirror al remoto (REQUIERE COORDINACIÓN):

```bash
git push --force
```

Riesgos y mitigaciones:
- Forzar push reescribe historia; romperá forks y clones. Mitigación: avisar al equipo, coordinar ventana de mantenimiento y pedir a todos que vuelvan a clonar.
- Pérdida accidental de commits raros si se borran objetos erróneos. Mitigación: generar una copia mirror antes y revisar cambios.
- Hooks/CI referenciando rutas antiguas pueden romper. Mitigación: revisar workflows y assets referenciados.

Checklist antes de ejecutar (obligatorio):
- [ ] Aprobar plan por el equipo (confirmación explícita)
- [ ] Backup: `git clone --mirror` del repo actual
- [ ] Identificar lista final de paths a eliminar
- [ ] Actualizar `.gitignore` (ya actualizado en este repo)
- [ ] Ajustar documentación y avisos en README/CONTRIBUTING

Contacto operativo: quien ejecute debe tener permisos de administrador del repositorio remoto.
