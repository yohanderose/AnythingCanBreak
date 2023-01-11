#include "WiFi.h"
#include "camera_index.h"
#include "esp_camera.h"
#include "esp_err.h"
#include "esp_http_server.h"
#include "fb_gfx.h"
#include "sensor.h"
#include "soc/rtc_cntl_reg.h" //disable brownout problems
#include "soc/soc.h"          //disable brownout problems
#include <Arduino.h>
#include <AsyncTCP.h>

#define CAMERA_MODEL_AI_THINKER // Has PSRAM

#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27

#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

#define LED_GPIO_NUM 33

#define PART_BOUNDARY "123456789000000000000987654321"
static const char *_STREAM_CONTENT_TYPE =
    "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char *_STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char *_STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: "
                                  "%u\r\nX-Timestamp: %d.%06d\r\n\r\n";

/* const char *ssid = "yohan_phone"; */
/* const char *pass = "testing123"; */
const char *ssid = "anythingcanbreaknet"; // your network SSID (name)
const char *pass = "48881722";            // your network password

int secondsElapsed = 0;
int deviceID = 2;

httpd_handle_t stream_httpd = NULL;

static esp_err_t remote_restart_handler(httpd_req_t *req) {
  char content[1024];
  sprintf(content, "Restarting %d", deviceID);
  httpd_resp_send(req, content, strlen(content));
  ESP.restart();
  return ESP_OK;
}

static esp_err_t device_id_handler(httpd_req_t *req) {
  char content[1024];
  sprintf(content, "Device ID: %d", deviceID);
  httpd_resp_send(req, content, strlen(content));
  return ESP_OK;
}

static esp_err_t stream_handler(httpd_req_t *req) {
  camera_fb_t *fb = NULL;
  esp_err_t res = ESP_OK;
  struct timeval _timestamp;
  int _jpg_buf_len = 0;
  uint8_t *_jpg_buf = NULL;
  char *part_buf[64];

  res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
  if (res != ESP_OK) {
    return res;
  }

  while (true) {
    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      res = ESP_FAIL;
    } else {
      /* Serial.println("Camera capture success"); */
      _timestamp.tv_sec = fb->timestamp.tv_sec;
      _timestamp.tv_usec = fb->timestamp.tv_usec;

      /* if (fb->width > 400) { */
      /*   if (fb->format != PIXFORMAT_JPEG) { */
      /*     bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
       */
      /*     esp_camera_fb_return(fb); */
      /*     fb = NULL; */
      /*     if (!jpeg_converted) { */
      /*       Serial.println("JPEG compression failed"); */
      /*       res = ESP_FAIL; */
      /*     } */
      /*   } else { */
      /*     _jpg_buf_len = fb->len; */
      /*     _jpg_buf = fb->buf; */
      /*   } */
      /* } */
      _jpg_buf_len = fb->len;
      _jpg_buf = fb->buf;
    }

    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY,
                                  strlen(_STREAM_BOUNDARY));
    }
    if (res == ESP_OK) {
      size_t hlen = snprintf((char *)part_buf, 128, _STREAM_PART, _jpg_buf_len,
                             _timestamp.tv_sec, _timestamp.tv_usec);
      res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
    }
    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
    }

    if (fb) {
      esp_camera_fb_return(fb);
      fb = NULL;
      _jpg_buf = NULL;
    } else if (_jpg_buf) {
      free(_jpg_buf);
      _jpg_buf = NULL;
    }
    if (res != ESP_OK) {
      log_e("Send frame failed");
      break;
    }

    /* Serial.printf("MJPG: %uB\n", (uint32_t)(_jpg_buf_len)); */
  }
  return res;
}

void startCameraServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80;

  httpd_uri_t index_uri = {.uri = "/",
                           .method = HTTP_GET,
                           .handler = stream_handler,
                           .user_ctx = NULL};

  httpd_uri_t device_id_uri = {.uri = "/id",
                               .method = HTTP_GET,
                               .handler = device_id_handler,
                               .user_ctx = NULL};

  httpd_uri_t restart_uri = {.uri = "/restart",
                             .method = HTTP_GET,
                             .handler = remote_restart_handler,
                             .user_ctx = NULL};

  // Serial.printf("Starting web server on port: '%d'\n", config.server_port);
  if (httpd_start(&stream_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(stream_httpd, &index_uri);
    httpd_register_uri_handler(stream_httpd, &device_id_uri);
    httpd_register_uri_handler(stream_httpd, &restart_uri);
  }
}

int connectToWiFi() {

  WiFi.mode(WIFI_STA);
  // check for the presence of the shield:
  /* if (WiFi.status() == WL_NO_SHIELD) { */
  /*   Serial.println("WiFi shield not present"); */
  /*   // don't continue: */
  /*   while (true) */
  /*     ; */
  /* } */

  Serial.print("Attempting to connect to WPA SSID: ");
  Serial.print(ssid);
  Serial.print(" ...");
  int attempts = 0;
  // attempt to connect to Wifi network:
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    if (attempts++ > 5) {
      Serial.println("FAILED");
      Serial.println("Restarting ESP32...");
      ESP.restart();
    }
    delay(5000);
    Serial.print(".");
  }
  Serial.println(" CONNECTED");

  return 0;
}

void setup() {
  pinMode(LED_GPIO_NUM, OUTPUT);

  Serial.begin(115200);
  /* Serial.setDebugOutput(true); */
  Serial.println();

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_240X240;
  config.pixel_format = PIXFORMAT_JPEG; // for streaming */
  // config.pixel_format = PIXFORMAT_RGB565; // for face detection
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 10;
  config.fb_count = 1;

  if (config.pixel_format == PIXFORMAT_JPEG) {
    if (psramFound()) {
      Serial.println("PSRAM found");
      config.jpeg_quality = 10;
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
      // Limit the frame size when PSRAM is not available
      /* config.frame_size = FRAMESIZE_SVGA; */
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  } else {
    // Best option for face detection/recognition
    /* config.frame_size = FRAMESIZE_240X240; */
#if CONFIG_IDF_TARGET_ESP32S3
    config.fb_count = 2;
#endif
  }

#if defined(CAMERA_MODEL_ESP_EYE)
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
#endif

  // camera init */
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
  sensor_t *s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);       // flip it back
    s->set_brightness(s, 1);  // up the brightness just a bit
    s->set_saturation(s, -2); // lower the saturation
  }
  // drop down frame size for higher initial frame rate
  if (config.pixel_format == PIXFORMAT_JPEG) {
    s->set_framesize(s, FRAMESIZE_QVGA);
  }
#if defined(CAMERA_MODEL_M5STACK_WIDE)
  defined(CAMERA_MODEL_M5STACK_ESP32CAM) s->set_vflip(s, 1);
  s->set_hmirror(s, 1);
#endif
#if defined(CAMERA_MODEL_ESP32S3_EYE)
  s->set_vflip(s, 1);
#endif

  // Init WiFi
  connectToWiFi();

  startCameraServer();
  /* int res = startCameraServer(); */
  /* if (res == 0) { */
  Serial.print("Device ID: ");
  Serial.println(deviceID);
  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");
  /* } else { */
  /*   Serial.println("Camera Server failed to start"); */
  /* } */
}

void loop() {

  // toggle led every 1 second
  digitalWrite(LED_GPIO_NUM, HIGH);
  delay(300);
  digitalWrite(LED_GPIO_NUM, LOW);
  delay(700);

  /* printf("seconds elapsed: %d", ++secondsElapsed); */
  /* Serial.println("seconds elapsed: " + String(++secondsElapsed)); */
}
