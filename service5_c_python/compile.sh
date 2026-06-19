#!/bin/bash
# compile.sh — Compile src/stats.c en bibliotheque partagee dans lib/
set -e

SRC_FILE="src/stats.c"
LIB_DIR="lib"
mkdir -p "${LIB_DIR}"

# Adapter l'extension, l'option de lien et les flags selon l'OS
# - macOS  : .dylib, -dynamiclib, -fPIC, -lm
# - Linux  : .so,    -shared,     -fPIC, -lm
# - Windows (MinGW/MSYS/Cygwin) : .dll, -shared, -lm (libm est un stub, sans danger),
#   PAS de -fPIC (ignoré sous MinGW : tout le code y est déjà position-independent)
FPIC="-fPIC"
LIBS="-lm"
case "$(uname -s)" in
    Darwin) OUT_FILE="${LIB_DIR}/stats.dylib"; SHARED="-dynamiclib" ;;
    MINGW*|MSYS*|CYGWIN*) OUT_FILE="${LIB_DIR}/stats.dll"; SHARED="-shared"; FPIC="" ;;
    *) OUT_FILE="${LIB_DIR}/stats.so"; SHARED="-shared" ;;
esac

echo "[1/2] Compilation de ${SRC_FILE} -> ${OUT_FILE}..."
gcc ${SHARED} ${FPIC} -O2 -Wall -o "${OUT_FILE}" "${SRC_FILE}" ${LIBS}

echo "[2/2] Bibliotheque creee : ${OUT_FILE}"
echo "Compilation reussie !"
