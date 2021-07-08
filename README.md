# evolution


# Build sundials 


    cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=../../sundials-install-mac ..
    cmake --build . --target install --config Release -j 12

This produces the standard sundials install tree inside the "sundials" folder.
