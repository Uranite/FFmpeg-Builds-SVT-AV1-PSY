#!/bin/bash

SCRIPT_REPO="https://code.videolan.org/videolan/libudfread.git"
SCRIPT_COMMIT="c3cd5cbb097924557ea4d9da1ff76a74620c51a8"

ffbuild_enabled() {
    return 0
}

ffbuild_dockerbuild() {
    ./bootstrap

    local myconf=(
        --prefix="$FFBUILD_PREFIX"
        --disable-shared
        --enable-static
        --with-pic
    )

    if [[ $TARGET == win* || $TARGET == linux* ]]; then
        myconf+=(
            --host="$FFBUILD_TOOLCHAIN"
        )
    else
        echo "Unknown target"
        return -1
    fi

    ./configure "${myconf[@]}"
    make -j$(nproc)
    make install DESTDIR="$FFBUILD_DESTDIR"

    ln -s libudfread.pc "$FFBUILD_DESTPREFIX"/lib/pkgconfig/udfread.pc
}
