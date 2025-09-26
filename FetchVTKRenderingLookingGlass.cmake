include(FetchContent)

if(NOT DEFINED vtkRenderingLookingGlass_SOURCE_DIR)
  set(proj vtkRenderingLookingGlass)
  set(EP_SOURCE_DIR "${CMAKE_BINARY_DIR}/${proj}")
  FetchContent_Populate(${proj}
    SOURCE_DIR     ${EP_SOURCE_DIR}
    GIT_REPOSITORY https://github.com/Kitware/LookingGlassVTKModule
    GIT_TAG        145e306d2f46808713d5b2b930ee5acbd6096a3e
    QUIET
    )
  message(STATUS "Remote - ${proj} [OK]")

  set(vtkRenderingLookingGlass_SOURCE_DIR ${EP_SOURCE_DIR})
endif()
message(STATUS "Remote - vtkRenderingLookingGlass_SOURCE_DIR:${vtkRenderingLookingGlass_SOURCE_DIR}")
