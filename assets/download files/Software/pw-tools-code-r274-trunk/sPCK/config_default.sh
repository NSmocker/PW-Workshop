#!/bin/bash

PKGNAME="spck"
PKGVERSION="3.0.2"
PKGSECTION="misc"
PKGAUTHOR="Ronny Wegener <wegener.ronny@gmail.com>"
PKGHOMEPAGE="http://sourceforge.net/p/pw-tools/doc/sPCK/"
PKGDEPENDS=""
PKGDESCRIPTION="Perfect World extraction/compression tool
 sPCK can extract, compress and add files from MMORPGs using
 the Angelica Engine (e.g. Perfect World).
 Supported are archives (*.pck) and patches (*.cup) up to 2 GB."

SRCPATTERN="*.cpp"
SRCDIR="src"
RCPATTERN=""
RCDIR=""
OBJDIR="obj"
DISTROOT="build/linux"
BINFILE="$DISTROOT/bin/$PKGNAME"

CC="g++"
CFLAGS="
    -c
    -Wall
    -O2
    $(wx-config --static=no --debug=no --cflags)
    "

RC=""
RCFLAGS=""

LD="g++"
LDFLAGS="-s"
LDLIBS="$(wx-config --static=no --debug=no --libs)"
