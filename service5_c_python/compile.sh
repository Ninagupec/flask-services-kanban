#!/bin/bash
# compile.sh — Compile src/stats.c en bibliotheque partagee dans lib/
set -e

SRC_FILE="src/stats.c"
LIB_DIR="lib"
mkdir -p "${LIB_DIR}"

# Adapter l'extension et l'option selon l'OS
case "$(uname -s)" in
    Darwin) OUT_FILE="${LIB_DIR}/stats.dylib"; SHARED="-dynamiclib" ;;
    MINGW*|MSYS*|CYGWIN*) OUT_FILE="${LIB_DIR}/stats.dll"; SHARED="-shared" ;;
    *) OUT_FILE="${LIB_DIR}/stats.so"; SHARED="-shared" ;;
esac

echo "[1/2] Compilation de ${SRC_FILE} -> ${OUT_FILE}..."
gcc ${SHARED} -fPIC -O2 -Wall -o "${OUT_FILE}" "${SRC_FILE}" -lm

echo "[2/2] Bibliotheque creee : ${OUT_FILE}"
echo "Compilation reussie !"
