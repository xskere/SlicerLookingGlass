include(FetchContent)

if(NOT DEFINED vtkRenderingLookingGlass_SOURCE_DIR)
  set(proj vtkRenderingLookingGlass)
  set(EP_SOURCE_DIR "${CMAKE_BINARY_DIR}/${proj}")
  FetchContent_Populate(${proj}
    SOURCE_DIR     ${EP_SOURCE_DIR}
    GIT_REPOSITORY https://github.com/xskere/LookingGlassVTKModule
    GIT_TAG        c0012e4a28faa59b067e24422cc92c6f1828528a
    QUIET
    )
  message(STATUS "Remote - ${proj} [OK]")

  set(vtkRenderingLookingGlass_SOURCE_DIR ${EP_SOURCE_DIR})
endif()
message(STATUS "Remote - vtkRenderingLookingGlass_SOURCE_DIR:${vtkRenderingLookingGlass_SOURCE_DIR}")
