cmake_minimum_required(VERSION 3.10)

set(PROJECT_NAME "weather")
project(${PROJECT_NAME} LANGUAGES CXX)

set(IMGUI_SRC src/imgui)

set(SOURCE_FILES
	src/main.cpp
	${IMGUI_SRC}/backends/imgui_impl_glfw.cpp
	${IMGUI_SRC}/backends/imgui_impl_opengl3.cpp
	${IMGUI_SRC}/imgui.cpp
	${IMGUI_SRC}/imgui_demo.cpp
	${IMGUI_SRC}/imgui_draw.cpp
	${IMGUI_SRC}/imgui_tables.cpp
	${IMGUI_SRC}/imgui_widgets.cpp
)
set(HEADER_FILES
)

if (UNIX AND NOT APPLE)
	set(LINUX TRUE)
	cmake_policy(SET CMP0072 NEW)
endif()

if (WIN32)
	set(ICON resources.rc)
elseif (APPLE)
	set(ICON icon.icns)
endif()

set(PRJ_ICON rc/${ICON})
set(PRJ_RESOURCES rc/settings.json)


set(LIBSUFFIX "a")

if (CMAKE_CXX_COMPILER_ID MATCHES "GNU")
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread -Wall")
elseif (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread -Wall")
elseif (CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /std:c++17")
	set(LIBSUFFIX "lib")
endif()
set(CMAKE_CXX_STANDARD 17)

#g++ -std=c++0x -I $LIBS/libpng -I $LIBS/zlib -pthread -Wall -g $SRC -lpthread -lGL -lGLU -lX11 $LIBS/libpng/libpng16.a $LIBS/zlib/libz.a -o 1;

if(MINGW OR MSVC)
	add_compile_definitions(WINDOWS_PLATFORM)
	set(ZLIB_NAME zlibstatic)
	set(JSONLIB_NAME jsoncpp)
	set(GLFW_NAME glfw3)
else()
	set(ZLIB_NAME libz)
	set(JSONLIB_NAME libjsoncpp)
	set(GLFW_NAME libglfw3)
endif()

set(LIBS "${CMAKE_CURRENT_SOURCE_DIR}/libs/lib")
set(LIBRARIES
	libcurl.${LIBSUFFIX}
	libcrypto.${LIBSUFFIX}
	libssl.${LIBSUFFIX}
	libtls.${LIBSUFFIX}
	${ZLIB_NAME}.${LIBSUFFIX}
	${JSONLIB_NAME}.${LIBSUFFIX}
	${GLFW_NAME}.${LIBSUFFIX}
)
set(LIBS_HEADERS 
	"${CMAKE_CURRENT_SOURCE_DIR}/libs/include"
	"${IMGUI_SRC}"
	"${IMGUI_SRC}/backends"
)

if(NOT MSVC)
	set(LIBRARIES -lm ${LIBRARIES})
else()
	set(LIBRARIES
		${LIBRARIES}
		Ws2_32.lib
		Wldap32.lib
		Bcrypt.lib
		Crypt32.lib
		Normaliz.lib
		opengl32.lib
		gdi32.lib
		shell32.lib
	)
	set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} /SUBSYSTEM:CONSOLE")
	add_compile_definitions(_UNICODE UNICODE)
endif()

if(LINUX)
	set(LIBRARIES ${LIBRARIES} -lrt -ldl -lGL -lX11)
endif(LINUX)

if(APPLE)
	set(CMAKE_EXE_LINKER_FLAGS "-framework Cocoa -framework IOKit")
endif(APPLE)

if(NOT MSVC)
	set(LIBRARIES  ${LIBRARIES} -lpthread)
endif()

add_compile_definitions(FILES_PREFIX="${CMAKE_CURRENT_SOURCE_DIR}")

message(STATUS "LIBRARIES ${LIBRARIES}")

include_directories(${LIBS_HEADERS})
link_directories(${LIBS})
add_executable(${PROJECT_NAME} WIN32 MACOSX_BUNDLE ${HEADER_FILES} ${SOURCE_FILES} ${PRJ_ICON} ${PRJ_RESOURCES})
target_link_libraries(${PROJECT_NAME} ${LIBRARIES})

if (APPLE)
	set_target_properties(${PROJECT_NAME} PROPERTIES MACOSX_BUNDLE_BUNDLE_NAME "${PROJECT_NAME}")

	set_source_files_properties(${PRJ_ICON}
								PROPERTIES
				MACOSX_PACKAGE_LOCATION "Resources")
	set_source_files_properties(${PRJ_RESOURCES}
								PROPERTIES
				MACOSX_PACKAGE_LOCATION "Resources/rc")
	set_target_properties(${PROJECT_NAME} PROPERTIES
						  MACOSX_BUNDLE_SHORT_VERSION_STRING "1.0.0"
						  MACOSX_BUNDLE_LONG_VERSION_STRING "1.0.0"
			  MACOSX_BUNDLE_ICON_FILE ${ICON} 
			  MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_SOURCE_DIR}/src/MacOSXBundleInfo.plist.in")
endif()
