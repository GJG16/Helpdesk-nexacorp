# Cómo detectar objetos grandes en el repo (análisis previo)

Estos comandos requieren una terminal Bash (Linux / WSL / Git Bash).

1) Clonar mirror (recomendado para análisis):

```bash
git clone --mirror https://github.com/your-org/your-repo.git repo.git
cd repo.git
```

2) Listar los 50 objetos más grandes (usa git verify-pack):

```bash
git gc --prune=now --aggressive
git verify-pack -v objects/pack/pack-*.idx | sort -k3 -n | tail -n 50
```

3) Alternativa (rev-list + cat-file):

```bash
git rev-list --objects --all > allfiles.txt
git cat-file --batch-check='%(objectsize:disk) %(objectname) %(rest)' < allfiles.txt \
  | sort -n -r | head -n 50 > large_objects.txt
```

4) Interpretar `large_objects.txt` para ver rutas y decidir qué eliminar (ej: `*.png`, `ui_steps/*`).

5) Preparar la lista final de paths a pasar a BFG o git filter-repo.

Notas:
- Estas operaciones son de lectura/diagnóstico; no modifican el remoto.
- Para la limpieza real, usar `git clone --mirror` y `bfg` o `git filter-repo` y revisar cuidadosamente antes de push forzado.
