# Skills

[English](../README.md) · [한국어](README_KO.md)

Claude Code를 비롯한 호환 AI 코딩 에이전트를 위한 개인 [Agent Skills](https://github.com/vercel-labs/skills) 모음입니다. 각 스킬은 `skills/<name>/SKILL.md`에 있습니다.

## 설치

[`skills`](https://github.com/vercel-labs/skills) CLI로 설치합니다(전역 설치 불필요).

전체 설치(대화형으로 선택):

```bash
npx skills add seonggukchoi/skills
```

또는 반복 사용 가능한 `--skill` 플래그로 원하는 스킬만 설치:

```bash
npx skills add seonggukchoi/skills --skill agent-creator --skill youtube-markdown
```

기타 명령: `npx skills list`, `npx skills update`, `npx skills remove <skill>`.

## 스킬

각 스킬은 개별적으로 설치할 수 있습니다:

| 스킬 | 설명 | 설치 |
| --- | --- | --- |
| [`agent-creator`](../skills/agent-creator) | AI 서브에이전트 프로필을 마크다운으로 설계·생성·진단·개선. | `npx skills add seonggukchoi/skills --skill agent-creator` |
| [`agent-instruction-management`](../skills/agent-instruction-management) | 에이전트 지침 파일(`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) 작성·리팩토링·관리. | `npx skills add seonggukchoi/skills --skill agent-instruction-management` |
| [`agent-orchestration`](../skills/agent-orchestration) | 여러 서브에이전트에 작업을 분배·병렬화하고 결과를 종합. | `npx skills add seonggukchoi/skills --skill agent-orchestration` |
| [`agent-organization-designer`](../skills/agent-organization-designer) | AI 에이전트 조직 설계·점검 — 어떤 에이전트가 필요한지, 역할 경계, 규모. | `npx skills add seonggukchoi/skills --skill agent-organization-designer` |
| [`bitwarden-cli`](../skills/bitwarden-cli) | Bitwarden CLI로 비밀번호·시크릿·메모·Send 관리(VaultWarden / 자체 호스팅 / REST 포함). | `npx skills add seonggukchoi/skills --skill bitwarden-cli` |
| [`codex-image-generation`](../skills/codex-image-generation) | Codex CLI 내장 `image_gen`으로 이미지 생성·편집(ChatGPT 구독 토큰, API 키 불필요). | `npx skills add seonggukchoi/skills --skill codex-image-generation` |
| [`doc-to-markdown`](../skills/doc-to-markdown) | 문서 파일(PDF, DOCX, PPTX, XLSX, HWP)을 깔끔한 마크다운으로 변환. | `npx skills add seonggukchoi/skills --skill doc-to-markdown` |
| [`watercrawl`](../skills/watercrawl) | self-hosted WaterCrawl API로 스크랩·크롤링·웹 검색(마크다운 출력, JS 렌더링, 스크린샷). | `npx skills add seonggukchoi/skills --skill watercrawl` |
| [`youtube-markdown`](../skills/youtube-markdown) | 유튜브 영상을 타임스탬프·화면 캡처가 포함된 검색 가능한 마크다운으로 변환. | `npx skills add seonggukchoi/skills --skill youtube-markdown` |

일부 스킬은 외부 도구가 필요합니다 — 예: `codex` CLI, Bitwarden `bw` CLI, `pandoc`, WaterCrawl 인스턴스(`watercrawl`용), 또는 Apple Silicon + `mlx-whisper`(`youtube-markdown`용). 각 스킬의 `SKILL.md`에서 사전 요구사항을 확인하세요.
