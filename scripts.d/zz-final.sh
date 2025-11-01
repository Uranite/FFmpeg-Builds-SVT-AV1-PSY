#!/bin/bash

SCRIPT_SKIP="1"

ffbuild_depends() {
    echo libiconv
    echo zlib
    echo fribidi
    echo gmp
    echo libxml2
    echo openssl
    echo xz
    echo fonts
    echo libvorbis
    echo opencl
    echo pulseaudio
    echo vmaf
    echo x11
    echo dav1d

    echo rpath
}

ffbuild_enabled() {
    return 0
}

ffbuild_dockerfinal() {
    return 0
}

ffbuild_dockerdl() {
    return 0
}

ffbuild_dockerlayer() {
    return 0
}

ffbuild_dockerstage() {
    return 0
}

ffbuild_dockerbuild() {
    return 0
}

ffbuild_ldexeflags() {
    return 0
}
