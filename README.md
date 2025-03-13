# New Google Calendar Slackbot

자료 조사: **2023-12-26 ~ 2023-12-29**  
개발 기간: **2024-01-02 ~ 2024-01-16**

---

## 📌 서비스 소개

### 🔹 개요

오늘의 일정 알림과 휴가 및 이벤트를 등록, 공유할 수 있는 **Google Calendar SlackBot**입니다.

---

## 🔥 Why New Google Calendar SlackBot? 

### 🚀 구글 캘린더 기본 제공 SlackBot vs New Google Calendar SlackBot 비교

| 기능 | 기본 제공 Google Calendar SlackBot | New Google Calendar SlackBot |
|------|------------------|----------------------------|
| **일정 조회** | `/gcal` 명령어로 일정 조회 | **자동 알림 + 클릭 한 번으로 조회 가능** |
| **일정 등록** | 캘린더에서 직접 입력해야 함 | **슬랙에서 바로 등록 가능** |
| **휴가 관리** | 일정 등록 후 수동 공유 | **휴가 등록 → 팀원 자동 공유** |
| **일정 전파** | 직접 캘린더 링크 복사 | **버튼 클릭 한 번으로 일정 공유** |
| **사용자 맞춤 설정** | 불가능 | **사용자별 알림 설정 가능 (추가 예정)** |
| **팀원과 연동** | 캘린더 링크 공유 필요 | **채널에 자동 공유 + 슬랙 알림** |


### ✅ **슬랙에서 바로 일정 등록 & 조회 가능**  
- **일정 등록:** 슬랙에서 바로 버튼 클릭으로 일정 추가  
- **일정 조회:** `/gcal` 없이도 **자동으로 오늘의 일정** 제공  

### ✅ **휴가 등록과 자동 공유**  
- 팀원이 휴가를 등록하면 **자동으로 슬랙에 공유**  
- 휴가 유형별(연차, 반차 등) **입력 폼이 최적화**  

### ✅ **손쉬운 일정 전파**  
- 일정이 있으면 **"내 일정 전파하기" 버튼으로 공유**  
- 공유된 일정은 **"(오늘)" 표시**가 추가되어 가시성 향상  

### ✅ **자동화된 알림 시스템**  
- 매일 **오전 9시, 오늘의 일정 자동 알림**  
- 특정 채널에 **중요 이벤트 자동 공지** 기능 추가 가능  

### ✅ **추가 확장 가능** (예정)  
- `/slash_command` 지원: `/create` 입력하면 일정 등록 모달 표시  
- 특정 날짜의 일정 조회 기능 추가  

---

Google Calendar의 기본 슬랙 연동은 단순 조회 수준이라 **팀 협업에는 부족**합니다.  
하지만 **My Google Calendar SlackBot**을 사용하면, **휴가 및 일정 등록, 조회, 전파**까지 모두 슬랙에서 해결 가능!  
👨‍💻 **팀원들과 실시간 공유가 필요한 환경**에서는 훨씬 더 편리하게 사용할 수 있습니다. 🚀

---

## 🖥️ 메인 화면

메인 화면에는 현재 사용 가능한 모든 기능이 배치되어 있으며,  
오늘 **휴가자 목록**과 **일정 목록**이 자동 갱신됩니다.

### ✅ 메인 화면 UI  
📷 **이미지:**  
![Untitled (2)](https://github.com/user-attachments/assets/7754b803-5ce5-42c5-a541-749d67d4ff86)

---

## 🏖️ 휴가 등록

멤버를 선택하여 자신의 캘린더에 **휴가를 등록**할 수 있습니다.  
선택한 휴가 종류(연차, 반차 등)에 따라 입력란이 다르게 표시됩니다.

### ✅ 연차 등록 UI  
📷 **이미지:**  
![Untitled (3)](https://github.com/user-attachments/assets/65267abd-3d6c-41c9-98aa-297eae28d165)  
![Untitled (4)](https://github.com/user-attachments/assets/db33f5ee-97bc-445e-81fd-e0617943c173)

### ✅ 반차, 시간 연차 등록 UI  
📷 **이미지:**  
![Untitled (5)](https://github.com/user-attachments/assets/e5e333d6-cabc-4daf-9020-0cdfe48dff2f)  
![Untitled (5-2)](https://github.com/user-attachments/assets/a755d9b6-6fcc-4559-a772-d26f3ff6c08c)

---

## 📅 이벤트 등록

일정을 입력하면 **구글 캘린더**에 자동으로 등록됩니다.  
"하루 종일" 체크 시 시간 입력란이 사라지고 날짜만 선택할 수 있습니다.

### ✅ 이벤트 입력 UI  
📷 **이미지:**  
![Untitled (6)](https://github.com/user-attachments/assets/30d26d98-e048-4c53-8028-62083aca5771)  
![Untitled (7)](https://github.com/user-attachments/assets/d454f196-1073-4191-99a6-34612b3afadf)

### ✅ 하루 종일 선택 시  
📷 **이미지:**  
![Untitled (8)](https://github.com/user-attachments/assets/3371ed59-4fb7-4bf2-b0e5-5ce0d290f898)

---

## ⏰ 오늘 일정 알림

슬랙봇이 매일 **오전 9시**에 오늘의 일정을 메시지로 알려줍니다.  
**유저별 알림 상세 설정** 기능은 향후 추가될 예정입니다.

### ✅ 일정 알림 메시지  
📷 **이미지:**  
![Untitled (9)](https://github.com/user-attachments/assets/b3932d9d-2da5-4ec4-850e-547df835d789)

---

## 🔄 일정 새로고침

**새로고침 버튼**을 눌러 오늘의 일정을 갱신할 수 있습니다.  
연차는 시간 없이, 반차나 시간 연차는 시간과 함께 표시됩니다.

### ✅ 일정 새로고침 UI  
📷 **이미지:**  
![Untitled (10)](https://github.com/user-attachments/assets/7b9de47e-2279-45b1-aa03-f6b09d97f6ed)

---

## 📢 이벤트 전파

"**내 일정 전파하기**" 기능을 통해 **다른 멤버**나 **채널**에 이벤트를 공유할 수 있습니다.  
전파된 일정이 오늘 날짜라면 **"(오늘)"**이 추가로 명시됩니다.

### ✅ 일정 전파하기 UI  
📷 **이미지:**  
![Untitled (11)](https://github.com/user-attachments/assets/68c00f15-0f5f-42f3-bdee-5a2ac714198b)

### ✅ 일정이 없을 경우  
📷 **이미지:**  
![Untitled (12)](https://github.com/user-attachments/assets/e9fe7527-ceb1-4d76-8e5b-e1ac24f29bb6)

### ✅ 슬랙봇 메시지 전파  
📷 **이미지:**  
![Untitled (13)](https://github.com/user-attachments/assets/ddeddf34-cc32-4bd6-b5a0-da4702e671b7)

---

## 📌 시스템 구성

슬랙봇의 전체적인 동작 흐름과 아키텍처를 설명합니다. Flask.ver, Fastapi.ver 둘 다 존재합니다.

### ✅ 시스템 아키텍처  
📷 **이미지:**  
![Untitled (16)](https://github.com/user-attachments/assets/48b66fc1-e947-4028-80c4-ea809eafd1c3)

---

## 🛠️ 서비스 시퀀스 다이어그램

각 기능별 **서비스 흐름**을 설명합니다.

### ✅ 구글 로그인 연동  
📷 **이미지:**  
![Untitled (17)](https://github.com/user-attachments/assets/c343de0d-f505-44ee-9159-90fd1de3bb74)

### ✅ 휴가 등록  
📷 **이미지:**  
![Untitled (18)](https://github.com/user-attachments/assets/ee7f22af-6292-4351-bf32-8e0550e9a409)

### ✅ 이벤트 등록  
📷 **이미지:**  
![Untitled (19)](https://github.com/user-attachments/assets/c9d7552b-8fa8-4b9d-9049-dc90af2d4fcb)

### ✅ 새로고침  
📷 **이미지:**  
![Untitled (20)](https://github.com/user-attachments/assets/a0c0a448-6ebc-415a-9f85-98557b1fd8c2)

### ✅ 이벤트 전파  
📷 **이미지:**  
![Untitled (21)](https://github.com/user-attachments/assets/bd66fca8-c7d9-4336-a67a-675b1c39adff)

### ✅ 전파된 이벤트 캘린더 추가  
📷 **이미지:**  
![Untitled (22)](https://github.com/user-attachments/assets/5424c71a-7713-4bf3-a0fa-5a5cb3a43393)

---

## 🧐 고민했던 점

- **UI/UX 개선**: 사용자 중심의 인터페이스 구성  
- **코드 재사용성 향상**: JSON 데이터 활용 및 휴먼 에러 최소화  

---

## 📌 추가할 기능 (TODO)

- UI 및 안내 텍스트 수정 및 보완  
- **유저별 알림 상세 설정 (DB 연동)**  
- 특정 날짜 일정 조회 기능  
- **캘린더 바로 가기 버튼** 추가  
- `/slash_command` 지원 (ex: `/create` → 일정 생성 모달)  
