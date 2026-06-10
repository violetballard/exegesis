Exegesis — macOS App Icon
=========================

This folder is a complete .iconset. To compile it into a .icns file,
keep the folder named "AppIcon.iconset" and run, from its parent dir:

    iconutil -c icns AppIcon.iconset

That produces AppIcon.icns, ready to drop into an .app bundle or an
Xcode asset catalog.

Vector sources (in /assets):
  exegesis-mark.svg      — the glyph alone, transparent background
  exegesis-appicon.svg   — the full 1024×1024 squircle icon

Contents (all generated from exegesis-appicon.svg):
  icon_16x16.png      16     icon_16x16@2x.png     32
  icon_32x32.png      32     icon_32x32@2x.png     64
  icon_128x128.png   128     icon_128x128@2x.png  256
  icon_256x256.png   256     icon_256x256@2x.png  512
  icon_512x512.png   512     icon_512x512@2x.png 1024
