#!/bin/sh
if [ "$#" -ne 1 ]; then
    echo "Uso: ${0##*/} ARCHIVOLATEX" >&2
    exit 1
fi
if ! [ -f "$1" ]; then
  echo "No se encuentra el archivo '$1'" >&2
  exit 1
fi
archivo_latex=$1
if echo "$archivo_latex" | grep "/" > /dev/null; then
    echo "La ruta de archivo incluye directorio/s"
    directorio="${archivo_latex%/*}"
else
    echo "La ruta de archivo es local"
    directorio=$(pwd -P)
fi
archivo_latex=${archivo_latex##*/}
cd "$directorio"
echo "Compilando '$archivo_latex' desde '$(pwd -P)' con latexmk..."
# argumentos de latexmk sacados del comando que tira TeXiFy IDEA
if latex -version | grep -i "miktex" > /dev/null; then
    # MiKTeX (normalmente en Windows/Mac)
    echo "Distribución de LaTeX: MiKTeX"
    # la salida se guarda en la carpeta 'out' dentro de la raiz del proyecto LaTeX actual (= '../out') y los archivos auxiliares en 'auxil' (= '../auxil')
    # si esas carpetas no existen se crean automáticamente
    if ! latexmk -pdf -file-line-error -interaction=nonstopmode -synctex=1 -output-format=pdf -output-directory=../out -aux-directory=../auxil "$archivo_latex"; then
        echo "Código de salida distinto de 0: hubieron errores"
    fi
else
    # TeX Live (normalmente en Linux)
    echo "Distribución de LaTeX: TeX Live"
    # ídem MiKTeX, sólo que no acepta -aux-directory (las salidas y auxiliares van todos en 'out')
    if ! latexmk -pdf -file-line-error -interaction=nonstopmode -synctex=1 -output-format=pdf -output-directory=../out "$archivo_latex"; then
        echo "Código de salida distinto de 0: hubieron errores"
    fi
fi
