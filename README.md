# Mapa conceptual: circuitería de entrada/salida (E/S)

Programa en **Python puro** (solo biblioteca estándar, sin instalar nada con pip) que dibuja un mapa conceptual
con estilo de plantilla colorida y lo guarda como imagen vectorial **SVG** en `salida/`.
Cada flecha lleva una palabra de enlace (concepto → enlace → concepto).

## Ejecución (Windows, PowerShell)

```powershell
python --version
python main.py
```

Genera `salida\mapa_conceptual_e_s.svg` y lo abre en el navegador. Para no abrirlo: `python main.py --no-abrir`.

## Cómo usar el resultado

- **Verlo / imprimirlo:** ábrelo en Edge o Chrome. Con Ctrl+P → "Guardar como PDF" obtienes un PDF.
- **Insertarlo en Word o PowerPoint:** Insertar → Imágenes → selecciona el `.svg`. Si necesitas PNG, clic derecho sobre la imagen → "Guardar como imagen" → PNG.

## Subir a GitHub

```powershell
git init
git add main.py requirements.txt README.md .gitignore salida
git commit -m "Mapa conceptual de la circuitería de E/S"
git branch -M main
git remote add origin URL_DE_MI_REPOSITORIO
git push -u origin main
```

Nota: "circuitería alternativa de E/S" no está definida en la instrucción; el mapa usa la circuitería y mecanismos generales de E/S.
