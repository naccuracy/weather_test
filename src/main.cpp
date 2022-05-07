//	  ☀️

#define CURL_STATICLIB
#include <algorithm>
#include <fstream>
#include <iostream>
#include <vector>
#include <string>

#include <openssl/hmac.h>
#include <curl/curl.h>
#include <json/json.h>

#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include <GLFW/glfw3.h> // Will drag system OpenGL headers

using namespace std;

vector<string> wind_speeds_descr = {
	u8"Менее 0.3",
	u8"0.3-3.4",
	u8"3.4-8.0",
	u8"8.0-10.8",
	u8"10.8-17.2",
	u8"17.2-24.5",
	u8"24.5-32.6",
	u8"Более 32.6"
};
///-----------------CURL {
string CA_PATH = "";

static size_t writer(char* data, size_t size, size_t nmemb, string& buffer) {
	size_t total_bytes = size * nmemb;
	//cout << "raw data: " << data << " size: " << total_bytes << endl;
	buffer.append(data, total_bytes);
	return total_bytes;
}

void get_weather(string lat, string lon, string& result) {
	char errorBuffer[CURL_ERROR_SIZE];
	string api_url = "http://www.7timer.info/bin/astro.php?lon=" + lon + "&lat=" + lat + "&product=astro&ac=0&unit=metric&output=json&tzshift=0";
	cout << "CURL request: " << api_url << endl;
	string header = "";

	CURL* curl_handle = curl_easy_init();
#ifdef WIN32
	if (!CA_PATH.empty()) {
		curl_easy_setopt(curl_handle, CURLOPT_CAINFO, CA_PATH.c_str());
	} else {
		cout << "ERROR: on Windows you need path to certificate .pem file!" << endl;
	}
#endif
	curl_easy_setopt(curl_handle, CURLOPT_URL, api_url.c_str());
	curl_easy_setopt(curl_handle, CURLOPT_WRITEFUNCTION, writer);
	curl_easy_setopt(curl_handle, CURLOPT_WRITEDATA, &result);
	curl_easy_setopt(curl_handle, CURLOPT_ERRORBUFFER, errorBuffer);

	if (!header.empty()) {
		struct curl_slist* chunk = nullptr;
		chunk = curl_slist_append(chunk, header.c_str());
		curl_easy_setopt(curl_handle, CURLOPT_HTTPHEADER, chunk);
	}

	CURLcode res = curl_easy_perform(curl_handle);
	if (res == CURLE_OK) {
		cout << "CURL Success" << endl;// res = " << result << endl;
	} else {
		cout << "CURL Error: er = " << errorBuffer << endl;
	}

	curl_easy_cleanup(curl_handle);
}

std:: string parse_weather_response(string& response) {
	Json::Value root;
	Json::Reader reader;
	reader.parse(response, root);
	//temperature C
	int mint = 100;
   	int maxt = -100;
	//wind v m/s
	int maxv = 0;
	//winds
	string winds = "";
	for(const auto& data: root["dataseries"]) {
		int t = data["temp2m"].asInt();
		mint = min(mint, t);
		maxt = max(maxt, t);
		const auto& wind = data["wind10m"];
		int vindex = wind["speed"].asInt();
		maxv = max(maxv, vindex);
		string dir = wind["direction"].asString();
		if (winds.find(dir) == string::npos) { winds += dir + ";"; }
	}
	string result = u8"Температура: " + to_string(mint) + "-" + to_string(maxt) + 
		u8"°C; Направление ветра: " + winds + u8" Скорость ветра: " + wind_speeds_descr[clamp(maxv-1, 0, static_cast<int>(wind_speeds_descr.size()))] + u8" м/сек.";
	//cout << "JSON res: " << result << endl;
	return result;
}
///-----------------CURL }



///-----------------IMGUI {
static void glfw_error_callback(int error, const char* description) {
	cout << "GLFW Error " << error << " - " << description << endl;
}
static void HelpMarker(const char* desc)
{
    ImGui::TextDisabled("(?)");
    if (ImGui::IsItemHovered())
    {
        ImGui::BeginTooltip();
        ImGui::PushTextWrapPos(ImGui::GetFontSize() * 35.0f);
        ImGui::TextUnformatted(desc);
        ImGui::PopTextWrapPos();
        ImGui::EndTooltip();
    }
}
///-----------------IMGUI }



int main(int argc, char* argv[]) {
#ifdef WIN32
	SetConsoleOutputCP(CP_UTF8);
	///--------------settings {
	cout << "read settings" << endl;
	ifstream settings_file;
	settings_file.open("rc/settings.json");
	Json::Value settings_root;
	Json::CharReaderBuilder builder;
	builder["collectComments"] = true;
	JSONCPP_STRING errs;
	if (!parseFromStream(builder, settings_file, &settings_root, &errs)) {
		cout << "JSON error: " << errs << endl;
		return 1;
	} else {
		CA_PATH = settings_root["cert_path"].asString();
		cout << " CA: " << CA_PATH << endl;
	}
	///--------------settings }
#endif
	///-----------------IMGUI {
	// Setup window
	glfwSetErrorCallback(glfw_error_callback);
	if (!glfwInit()) {
		return 1;
	}
	// Decide GL+GLSL versions
#if defined(IMGUI_IMPL_OPENGL_ES2)
	// GL ES 2.0 + GLSL 100
	const char* glsl_version = "#version 100";
	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 2);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
	glfwWindowHint(GLFW_CLIENT_API, GLFW_OPENGL_ES_API);
#elif defined(__APPLE__)
	// GL 3.2 + GLSL 150
	const char* glsl_version = "#version 150";
	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 2);
	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);  // 3.2+ only
	glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);			// Required on Mac
#else
	// GL 3.0 + GLSL 130
	const char* glsl_version = "#version 130";
	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
	//glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);  // 3.2+ only
	//glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);			// 3.0+ only
#endif
	// Create window with graphics context
	//#set(PROJECT_NAME "weather") from CMakeList
	GLFWwindow* window = glfwCreateWindow(1280, 720, "Weather", NULL, NULL);
	if (window == nullptr) {
		return 1;
	}
	glfwMakeContextCurrent(window);
	glfwSwapInterval(1); // Enable vsync
	// Setup Dear ImGui context
	IMGUI_CHECKVERSION();
	ImGui::CreateContext();
	ImGuiIO& io = ImGui::GetIO(); (void)io;
	// Setup Dear ImGui style
	ImGui::StyleColorsDark();
	// Setup Platform/Renderer backends
	ImGui_ImplGlfw_InitForOpenGL(window, true);
	ImGui_ImplOpenGL3_Init(glsl_version);
	//Setup font
	ImFont* font = io.Fonts->AddFontFromFileTTF("rc/XO_Tahion_Nu.ttf", 16.0f, nullptr, io.Fonts->GetGlyphRangesCyrillic());
	if (font == nullptr) {
		cout << "WARRNING: font is nullptr!";
	}
	// Our state
	ImGuiTextBuffer MemoData;
	ImVec4 clear_color = ImVec4(0.45f, 0.55f, 0.60f, 1.00f);
	char place[2][16] = { "60", "30.5" };
	// Main loop
	while (!glfwWindowShouldClose(window))
	{
		// Poll and handle events (inputs, window resize, etc.)
		// You can read the io.WantCaptureMouse, io.WantCaptureKeyboard flags to tell if dear imgui wants to use your inputs.
		// - When io.WantCaptureMouse is true, do not dispatch mouse input data to your main application.
		// - When io.WantCaptureKeyboard is true, do not dispatch keyboard input data to your main application.
		// Generally you may always pass all inputs to dear imgui, and hide them from your application based on those two flags.
		glfwPollEvents();
		// Start the Dear ImGui frame
		ImGui_ImplOpenGL3_NewFrame();
		ImGui_ImplGlfw_NewFrame();
		ImGui::NewFrame();
///--------------------------------------FORM1 {
		{
			ImGui::Begin(u8"Погода");
			ImGui::Text(u8"Запросить данные 7timer.info при помощи CURL");
			ImGui::PushItemWidth(150);
			ImGui::InputText(u8"Широта:", place[0], IM_ARRAYSIZE(place[0]));
			ImGui::SameLine(); HelpMarker(u8"latitude");
			ImGui::InputText(u8"Долгота:", place[1], IM_ARRAYSIZE(place[1]));
			ImGui::SameLine(); HelpMarker(u8"lontitude");
			ImGui::PopItemWidth();

			if (ImGui::Button(u8"Запрос")) {
				string weather = "";
				get_weather(place[0], place[1], weather);
				string res = parse_weather_response(weather);
				MemoData.appendf(u8"Результат запроса: %s\n", res.c_str());
			}
			ImGui::SameLine();
			if (ImGui::Button(u8"Очистить лог")) {
				MemoData.clear();
			}

			ImGui::BeginChild(u8"Лог");
			ImGui::TextUnformatted(MemoData.begin(), MemoData.end());
			ImGui::EndChild();
			ImGui::End();
		}
///--------------------------------------FORM1 }
		// Rendering
		ImGui::Render();
		int display_w, display_h;
		glfwGetFramebufferSize(window, &display_w, &display_h);
		glViewport(0, 0, display_w, display_h);
		glClearColor(clear_color.x * clear_color.w, clear_color.y * clear_color.w, clear_color.z * clear_color.w, clear_color.w);
		glClear(GL_COLOR_BUFFER_BIT);
		ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
		glfwSwapBuffers(window);
	}
	// Cleanup
	ImGui_ImplOpenGL3_Shutdown();
	ImGui_ImplGlfw_Shutdown();
	ImGui::DestroyContext();
	glfwDestroyWindow(window);
	glfwTerminate();
///-----------------IMGUI }
	return 0;
}

