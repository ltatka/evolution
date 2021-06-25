# ---------------------------------------------------------------
# Programmer(s): Cody J. Balos @ LLNL
# ---------------------------------------------------------------
# SUNDIALS Copyright Start
# Copyright (c) 2002-2021, Lawrence Livermore National Security
# and Southern Methodist University.
# All rights reserved.
#
# See the top-level LICENSE and NOTICE files for details.
#
# SPDX-License-Identifier: BSD-3-Clause
# SUNDIALS Copyright End
# ---------------------------------------------------------------

include(CMakeFindDependencyMacro)
include("${CMAKE_CURRENT_LIST_DIR}/SUNDIALSTargets.cmake")

### ------- Alias targets
set(_SUNDIALS_ALIAS_TARGETS "sundials_kinsol->sundials_kinsol_shared;sundials_idas->sundials_idas_shared;sundials_ida->sundials_ida_shared;sundials_cvodes->sundials_cvodes_shared;sundials_cvode->sundials_cvode_shared;sundials_arkode->sundials_arkode_shared;sundials_sunnonlinsolfixedpoint->sundials_sunnonlinsolfixedpoint_shared;sundials_sunnonlinsolnewton->sundials_sunnonlinsolnewton_shared;sundials_sunlinsolsptfqmr->sundials_sunlinsolsptfqmr_shared;sundials_sunlinsolspgmr->sundials_sunlinsolspgmr_shared;sundials_sunlinsolspfgmr->sundials_sunlinsolspfgmr_shared;sundials_sunlinsolspbcgs->sundials_sunlinsolspbcgs_shared;sundials_sunlinsolpcg->sundials_sunlinsolpcg_shared;sundials_sunlinsoldense->sundials_sunlinsoldense_shared;sundials_sunlinsolband->sundials_sunlinsolband_shared;sundials_sunmatrixsparse->sundials_sunmatrixsparse_shared;sundials_sunmatrixdense->sundials_sunmatrixdense_shared;sundials_sunmatrixband->sundials_sunmatrixband_shared;sundials_nvecmanyvector->sundials_nvecmanyvector_shared;sundials_nvecserial->sundials_nvecserial_shared;sundials_generic->sundials_generic_shared;")
foreach(ptr ${_SUNDIALS_ALIAS_TARGETS})
  string(REGEX REPLACE "sundials_" "" ptr "${ptr}")
  string(REGEX MATCHALL "([A-Za-z_]+)->([A-Za-z_]+)"
         _matches "${ptr}")
  set(_pointer ${CMAKE_MATCH_1})
  set(_pointee ${CMAKE_MATCH_2})
  set_target_properties(SUNDIALS::${_pointee} PROPERTIES IMPORTED_GLOBAL TRUE)
  add_library(SUNDIALS::${_pointer} ALIAS SUNDIALS::${_pointee})
endforeach()

### ------- Create TPL imported targets

if(OFF AND NOT TARGET SUNDIALS::HYPRE)
  add_library(SUNDIALS::HYPRE INTERFACE IMPORTED GLOBAL)
  target_link_libraries(SUNDIALS::HYPRE INTERFACE "")
  set_target_properties(SUNDIALS::HYPRE PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "")
endif()

if(OFF AND NOT TARGET SUNDIALS::KLU)
  add_library(SUNDIALS::KLU INTERFACE IMPORTED GLOBAL)
  target_link_libraries(SUNDIALS::KLU INTERFACE "")
  set_target_properties(SUNDIALS::KLU PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "")
endif()

if(OFF)
  set(PETSC_LIBRARY_SINGLE "")
  if(${PETSC_LIBRARY_SINGLE})
    foreach(suffix SYS VEC MAT DM KSP SNES TS ALL)
      if(NOT TARGET SUNDIALS::PETSC_${suffix})
        add_library(SUNDIALS::PETSC_${suffix} UNKNOWN IMPORTED)
        set_target_properties(SUNDIALS::PETSC_${suffix} PROPERTIES
          INTERFACE_INCLUDE_DIRECTORIES "")
        set_target_properties(SUNDIALS::PETSC_${suffix} PROPERTIES
          INTERFACE_LINK_LIBRARIES "")
        set_target_properties(SUNDIALS::PETSC_${suffix} PROPERTIES
          INTERFACE_COMPILE_OPTIONS "")
        set_target_properties(SUNDIALS::PETSC_${suffix} PROPERTIES
          IMPORTED_LOCATION "${PETSC_LIBRARY_SINGLE}")
      endif()
    endforeach()
  else()
    set(PESTC_LIBRARY_SYS "")
    set(PESTC_LIBRARY_VEC "")
    set(PESTC_LIBRARY_MAT "")
    set(PESTC_LIBRARY_DM "")
    set(PESTC_LIBRARY_KSP "")
    set(PESTC_LIBRARY_SNES "")
    set(PESTC_LIBRARY_TS "")
    set(PESTC_LIBRARY_ALL "")

    set(PESTC_LIBRARIES_SYS "")
    set(PESTC_LIBRARIES_VEC "")
    set(PESTC_LIBRARIES_MAT "")
    set(PESTC_LIBRARIES_DM "")
    set(PESTC_LIBRARIES_KSP "")
    set(PESTC_LIBRARIES_SNES "")
    set(PESTC_LIBRARIES_TS "")
    set(PESTC_LIBRARIES_ALL "")

    foreach(suffix SYS VEC MAT DM KSP SNES TS ALL)
      if(NOT TARGET SUNDIALS::PETSC_${suffix})
        add_library(SUNDIALS::PETSC_${suffix} UNKNOWN IMPORTED)
        set_target_properties (SUNDIALS::PETSC_${suffix} PROPERTIES
          INTERFACE_INCLUDE_DIRECTORIES "")
        set_target_properties (SUNDIALS::PETSC_${suffix} PROPERTIES
          INTERFACE_LINK_LIBRARIES "${PETSC_LIBRARIES_${suffix}}")
        set_target_properties (SUNDIALS::PETSC_${suffix} PROPERTIES
          INTERFACE_COMPILE_OPTIONS "${PETSC_DEFINITIONS}")
        set_target_properties (SUNDIALS::PETSC_${suffix} PROPERTIES
          IMPORTED_LOCATION "${PETSC_LIBRARY_${suffix}}")
      endif()
    endforeach()
  endif()
endif()

if(OFF AND NOT TARGET SUNDIALS::MAGMA)
  add_library(SUNDIALS::MAGMA INTERFACE IMPORTED GLOBAL)
  target_link_libraries(SUNDIALS::MAGMA INTERFACE "")
  set_target_properties(SUNDIALS::MAGMA PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "")
endif()

if(OFF AND NOT TARGET SUNDIALS::SUPERLUDIST)
  add_library(SUNDIALS::SUPERLUDIST INTERFACE IMPORTED GLOBAL)
  target_link_libraries(SUNDIALS::SUPERLUDIST INTERFACE "")
  set_target_properties(SUNDIALS::SUPERLUDIST PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "")
endif()

if(OFF AND NOT TARGET SUNDIALS::SUPERLUMT)
  add_library(SUNDIALS::SUPERLUMT INTERFACE IMPORTED GLOBAL)
  target_link_libraries(SUNDIALS::SUPERLUMT INTERFACE "")
  set_target_properties(SUNDIALS::SUPERLUMT PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "")
endif()

if(OFF AND NOT TARGET RAJA)
  find_package(RAJA PATHS )
endif()

if(OFF AND NOT TARGET SUNDIALS::TRILINOS)
  add_library(SUNDIALS::TRILINOS INTERFACE IMPORTED GLOBAL)
  target_link_libraries(SUNDIALS::TRILINOS INTERFACE "")
  set_target_properties(SUNDIALS::TRILINOS PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "")
endif()

if(OFF AND NOT TARGET SUNDIALS::XBRAID)
  add_library(SUNDIALS::XBRAID INTERFACE IMPORTED GLOBAL)
  target_link_libraries(SUNDIALS::XBRAID INTERFACE "")
  set_target_properties(SUNDIALS::XBRAID PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "")
endif()
