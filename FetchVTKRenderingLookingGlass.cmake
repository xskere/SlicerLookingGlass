include(FetchContent)

if(NOT DEFINED vtkRenderingLookingGlass_SOURCE_DIR)
  set(proj vtkRenderingLookingGlass)
  set(EP_SOURCE_DIR "${CMAKE_BINARY_DIR}/${proj}")
  FetchContent_Populate(${proj}
    SOURCE_DIR     ${EP_SOURCE_DIR}
    GIT_REPOSITORY https://github.com/xskere/LookingGlassVTKModule
    GIT_TAG        b4e8191b3ccb566d6d2f6e2ce8c564a30bfc5181
    QUIET
    )
  message(STATUS "Remote - ${proj} [OK]")

  set(vtkRenderingLookingGlass_SOURCE_DIR ${EP_SOURCE_DIR})
endif()
message(STATUS "Remote - vtkRenderingLookingGlass_SOURCE_DIR:${vtkRenderingLookingGlass_SOURCE_DIR}")
