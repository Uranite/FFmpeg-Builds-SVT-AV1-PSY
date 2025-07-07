#!/bin/bash

package_variant() {
    IN="$1"
    OUT="$2"

    # Copy the executables
    mkdir -p "$OUT"/bin
    cp "$IN"/bin/* "$OUT"/bin

    # Copy the static libraries
    mkdir -p "$OUT"/lib
    cp -a "$IN"/lib/*.a "$OUT"/lib

    # Copy the pkg-config files
    mkdir -p "$OUT"/lib/pkgconfig
    cp -a "$IN"/lib/pkgconfig/*.pc "$OUT"/lib/pkgconfig

    # Copy the header files
    mkdir -p "$OUT"/include
    cp -r "$IN"/include/* "$OUT"/include

    # Copy the docs
    mkdir -p "$OUT/doc"
    cp -r "$IN"/share/doc/ffmpeg/* "$OUT"/doc
}
