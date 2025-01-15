#!/bin/bash

SCRIPT_REPO="https://github.com/google/shaderc.git"
SCRIPT_COMMIT="690d259384193c90c01b52288e280b05a8481121"

ffbuild_enabled() {
    [[ $ADDINS_STR == *4.4* ]] && return -1
    return 0
}

ffbuild_dockerdl() {
    default_dl .
    echo "./utils/git-sync-deps"
}

ffbuild_dockerbuild() {
    mkdir build && cd build

    cmake \
        -DCMAKE_TOOLCHAIN_FILE="$FFBUILD_CMAKE_TOOLCHAIN" \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX="$FFBUILD_PREFIX" \
        -DBUILD_SHARED_LIBS=OFF \
        -DENABLE_GLSLANG_BINARIES=OFF \
        -DSHADERC_ENABLE_WERROR_COMPILE=OFF \
        -DSHADERC_SKIP_{COPYRIGHT_CHECK,EXAMPLES,TESTS}=ON \
        -DSPIRV_{TOOLS_BUILD_STATIC,SKIP_EXECUTABLES}=ON \
        -DSPIRV_WERROR=OFF \
        -GNinja \
        ..
    ninja -j$(nproc)
    ninja install

    # for some reason, this does not get installed...
    cp libshaderc_util/libshaderc_util.a "$FFBUILD_PREFIX"/lib

    echo "Libs: -lstdc++" >> "$FFBUILD_PREFIX"/lib/pkgconfig/shaderc_combined.pc
    echo "Libs: -lstdc++" >> "$FFBUILD_PREFIX"/lib/pkgconfig/shaderc_static.pc

    cp "$FFBUILD_PREFIX"/lib/pkgconfig/{shaderc_combined,shaderc}.pc

    if [[ $TARGET == win* ]]; then
        rm -r "$FFBUILD_PREFIX"/bin "$FFBUILD_PREFIX"/lib/*.dll.a
    elif [[ $TARGET == linux* ]]; then
        rm -r "$FFBUILD_PREFIX"/bin "$FFBUILD_PREFIX"/lib/*.so*
    else
        echo "Unknown target"
        return -1
    fi
}

ffbuild_configure() {
    echo --enable-libshaderc
}

ffbuild_unconfigure() {
    [[ $ADDINS_STR == *4.4* ]] && return 0
    echo --disable-libshaderc
}
