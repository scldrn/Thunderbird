import os
import shutil

src_root = "entradas"
dst_root = "salidas/prueba"

os.makedirs(dst_root, exist_ok=True)

copied = []

for root, dirs, files in os.walk(src_root):
    for f in files:
        src_path = os.path.join(root, f)
        rel_path = os.path.relpath(src_path, src_root)
        
        # 1. Copia preservando estructura relativa
        tree_dst = os.path.join(dst_root, rel_path)
        os.makedirs(os.path.dirname(tree_dst), exist_ok=True)
        shutil.copyfile(src_path, tree_dst)
        copied.append((src_path, tree_dst, oct(os.stat(tree_dst).st_mode)))
        
        # 2. Copia plana directamente en salidas/prueba
        flat_dst = os.path.join(dst_root, f)
        shutil.copyfile(src_path, flat_dst)
        copied.append((src_path, flat_dst, oct(os.stat(flat_dst).st_mode)))

print(f"Copiados exitosamente {len(copied)} destinos con shutil.copyfile:")
for s, d, m in copied:
    print(f"  {s} -> {d} (permisos: {m})")
