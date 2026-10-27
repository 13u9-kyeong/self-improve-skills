# selfimprove

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Claude Code skill](https://img.shields.io/badge/Claude%20Code-skill%20%2B%20plugin-8A63D2.svg)

**에이전트 파이프라인이 정말 나아졌는지 숫자로 확인하면서 개선하는 루프를 만들어 주는 Claude Code
스킬입니다. 도메인은 가리지 않습니다. 사용자와 인터뷰하면서 채점 계층과 게이트를 만들고, 라운드마다
결과를 채점합니다.**

[English README](README.md)

```
/selfimprove "an agent that extracts fields from supplier invoices, built from our AP archive"
```

에이전트 파이프라인의 "개선"은 대개 누군가 결과물을 다시 읽어 보고 좋아진 것 같다고 느끼는 데서
끝납니다. 이 스킬은 그런 판단을 인정하지 않습니다. 라운드가 의미 있으려면 **틀렸을 때 그 사실이
누구도 반박하지 못할 만큼 분명하게 드러나야** 하고, 그러려면 세 가지가 필요합니다.

1. **파이프라인이 볼 수 없었던 키(정답).** 시간이 지나 확정됐거나 제3자가 봉인한 것이어야 합니다.
   직접 골라 둔 홀드아웃 세트는 키가 되지 못합니다.
2. **도메인 고유의 가치 단위로 채점하는 스코어러.** *찾은 것*과 *전달된 것*, 두 숫자를 항상 따로
   보고하고 하나로 합치지 않습니다.
3. **실행 전에 남긴 기록.** 어떤 결과가 나오면 실패로 볼지 미리 적어 둡니다.

스킬은 사용자와 함께 결정을 하나씩 내리면서 이 세 가지를 만듭니다. 그다음 라운드를 돌려 지표의
상한, 곧 천장을 정하는 단계 하나를 찾고 라운드마다 한 가지만 바꿉니다. 도메인에 그런 키가 없으면
점수를 지어내는 대신 키가 없다고 알려 줍니다.

---

## 목차

- [설치](#설치)
- [빠른 시작](#빠른-시작)
- [사용 예시](#사용-예시)
- [동작 방식](#동작-방식)
- [하지 않는 일](#하지-않는-일)
- [설치되는 파일](#설치되는-파일)
- [도메인 계층](#도메인-계층)
- [도구와 종료 코드 규칙](#도구와-종료-코드-규칙)
- [노력 배분 우선순위](#노력-배분-우선순위)
- [기여](#기여) · [라이선스](#라이선스)

---

## 설치

요구 사항: [Claude Code](https://claude.com/claude-code), Python 3.9+,
[PyYAML](https://pypi.org/project/PyYAML/) (`pip install pyyaml`).

### 플러그인으로 설치 (권장)

Claude Code 안에서:

```
/plugin marketplace add https://github.com/13u9-kyeong/self-improve-skills.git
/plugin install selfimprove@selfimprove
```

또는 셸에서:

```bash
claude plugin marketplace add https://github.com/13u9-kyeong/self-improve-skills.git
claude plugin install selfimprove@selfimprove
```

플러그인 스킬에는 네임스페이스가 붙기 때문에 **`/selfimprove:selfimprove`**로 호출합니다. 특정
릴리스로 고정하려면 저장소 URL 뒤에 `#v1.0.0`을 붙이세요. 이 저장소는 GitHub 비공개 저장소라서,
`/plugin`을 쓰기 전에 `git`으로 저장소를 clone할 수 있는 상태여야 합니다(예: `gh auth login` 후
`gh auth setup-git`).

### 단독 스킬로 설치

```bash
git clone https://github.com/13u9-kyeong/self-improve-skills.git
self-improve-skills/install.sh              # all projects -> ~/.claude/skills/selfimprove/
self-improve-skills/install.sh --project    # this project -> ./.claude/skills/selfimprove/
```

**`/selfimprove`**로 호출합니다. 업데이트할 때는 pull한 뒤 `install.sh`를 다시 실행하세요. 설치본이
통째로 교체됩니다.

어느 방식으로 설치하든 키트 전체는 스킬 디렉터리의 `kit/`에 들어 있습니다. 프로젝트에서 스킬을 처음
호출하면 키트를 그 프로젝트에 설치해도 되는지 먼저 묻습니다. 기존 파일은 절대 덮어쓰지 않습니다.
프로젝트에 이미 `CLAUDE.md`가 있으면 루프 규칙을 `# Self-improvement loop` 제목 아래에 덧붙이고
바뀐 내용을 diff로 보여 줍니다.

---

## 빠른 시작

1. 에이전트가 일할 프로젝트에서 Claude Code를 엽니다.
2. 원하는 것을 한 문장으로 말합니다: `/selfimprove "X를 하는 에이전트, Y 기반으로"`.
3. 질문 여섯 개에 답합니다. 질문마다 구체적인 선택지가 2–4개 나옵니다. 추천안이 맨 앞에 있고
   선택지마다 그걸 고르면 무엇을 측정하지 못하게 되는지 적혀 있습니다.
4. 스킬이 계층과 게이트를 다 만들고 나면, 라운드를 더 돌리고 싶을 때마다 "다음 라운드 돌려"라고
   말합니다.

언제든 멈춰도 됩니다. 다음 주에 `/selfimprove`를 다시 호출하면, 아직 답하지 않은 질문이나 체크하지
않은 항목 중 첫 번째부터 이어서 진행합니다.

**이럴 때 쓰세요.** 반복되는 작업에서 에이전트가 얼마나 나아지는지 숫자로 확인하고 싶을 때입니다.
예를 들면:

- 변경 이력이 공개된 코드베이스에서 버그 수정이나 테스트 작성
- 문서에서 구조화된 데이터 추출, 분류, 라벨링
- 예측, 데이터 분석, 포맷이나 프로토콜의 스펙 적합성 작업
- 그 밖에 무엇을 "완료"로, 무엇을 "증거"로 볼지 정할 수 있는 작업

**이럴 때는 쓰지 마세요.** 한 번 하고 끝나는 작업입니다. 채점하는 라운드를 반복하지 않으면 루프가
개선할 대상이 없습니다.

---

## 사용 예시

도메인과 답변은 예시로 지어낸 것이지만, 진행 흐름은 스킬이 실제로 하는 그대로입니다. (아래 기록은
영문판과 똑같이 유지하려고 번역하지 않았습니다.)

```
you   /selfimprove "an agent that extracts invoice fields, from our accounts-payable archive"

      [step 0]  loop_state.py -> kit not installed
skill The kit isn't in this project yet. It adds CLAUDE.md at the root (loaded into every
      session), plus scripts/, harness/, templates/, domains/. Install?
you   yes

      [setup:interview — goal]
skill Restating: the work is "fill the invoice schema from one scanned invoice"; success
      means "every field matches what the clerk posted to the ledger". Correct?
you   yes

      [setup:interview — material]   (the skill reads the archive first)
skill Found 41,200 invoices, OCR text for 38,900, received dates for all of them,
      and 1,140 invoices posted by clerks after the model's training cutoff.
        candidate key:   the 1,140 clerk-posted ledger entries (sealed by another party)
        raw material:    everything else

      [setup:interview — denominator]   AskUserQuestion
        > schema field × invoice   (Recommended)
            complete when every (field, invoice) cell has a disposition;
            give-up bucket: pages the OCR step could not read
        > line item × invoice
            enumerable, but misses header fields (totals, tax, terms)
        > the 41,200 invoices
            this is a sample, not a denominator — coverage would be unmeasurable

      [setup:interview — verdict]       one question per lens family
      [setup:interview — key]           inventory, sealing, training cutoff
      [setup:interview — delivered]     the hardest definition the destination offers

      [setup:phase0]
skill 0.1 passes: 1,140 post-cutoff invoices with clerk-posted entries. 0.2 passes after
      reproducing one month's reconciliation by hand. 0.3 passes: exact match by script.

      [setup:layer]  shows the stage table and lens families once, then writes
                     SURFACE / VERDICTS / STAGES / lenses / config / one agent per stage
      [setup:gates]  writes each gate, gives each a real failing input,
                     sabotage-verifies them, conformance test green

      [round:baseline]
skill Round 1 target: 60 unspent invoices from SEALED.md. Preregistration written, key moved
      out of the tree, target read-only. Running…
      compare: 41/60 success · failures: input_misread 9 at [3], reasoning_error 6 at [5]
      found 41/60 · delivered 29/60 · loss by stage: [6] grading 8, [7] delivery 4
      ceiling: 15 of 19 misses never appear in any artifact -> ceiling is [3] intake

      [round:next]
skill Proposed change for round 2: the one at [3] intake. A change at [6] could raise the
      delivered count but cannot raise recall, because recall is capped at [3]. Proceed?
```

---

## 동작 방식

### 루프

에이전트가 처음 보는 문제를 풉니다. 답은 미리 정해 둔 규칙에 따라 같은 문제의 정답과 하나씩
비교합니다. 정답으로는 과거 보고서나 정답지를 씁니다. 틀린 문제마다 이유를 붙이고 천장 단계에서
가장 많이 나온 이유를 고친 다음, 새 문제로 다음 라운드를 돌립니다.

```
 problem ──▶ agent pipeline ──▶ answer
                                  │
 key (past report / answer sheet) ┴─▶ compare.py ──▶ success | failure
                                                          │
                       failure-analyst ──▶ failures.py ◀──┘   class · stage · cause
                                                │
            one change at the ceiling stage ◀───┘   (card + check, sabotage-verified)
                          │
                          └──▶ next round on unseen problems
```

### 단계 판별

스킬은 호출될 때마다 `scripts/loop_state.py`를 실행합니다. 이 스크립트가 프로젝트 파일을 읽고 지금
실행할 단계를 알려 줍니다. 이 규칙들은 과거 기록에서 나왔습니다. 그 기록을 보면 오케스트레이터가
실패한 경우는 모두 같은 유형이었는데, 파일 생김새만 보고 지금 어느 단계인지 짐작했습니다.

| 단계 | 진입 조건 | 하는 일 |
|---|---|---|
| `setup:interview` | `INTERVIEW.md`가 없거나, 아직 답하지 않은 결정이 남음 | 사용자와 여섯 가지를 결정하고 기록 |
| `setup:phase0` | 인터뷰 완료, 체크하지 않은 하드 게이트가 있고 결정 기록이 없음 | 하드 게이트 세 개 확인. 하나라도 실패하면 사용자가 결정 |
| `setup:layer` | Phase 0 결정 완료, `new_domain.py --check`가 아직 계층을 통과시키지 않음 | surface, verdicts, stages, 에이전트, lenses, config 작성 |
| `setup:gates` | 계층 완성, 설정한 gate 중 스크립트가 없는 것이 있음 | gate 스크립트, conformance 테스트, 사보타주 검사 |
| `round:baseline` | 모두 준비됨, 채점한 라운드 없음 | 라운드 1: 아무것도 바꾸지 않고 천장만 찾음 |
| `round:in-progress` | `ROUND.md`는 있는데 `RESULT.md`가 없는 라운드가 있음 | 체크하지 않은 첫 항목부터 이어서 진행 |
| `round:next` | 채점한 라운드가 하나 이상 | 천장 단계에서 바꿀 것 하나를 골라 다음 라운드 진행 |

### 사용자와 정하는 여섯 가지

```
goal -> material -> denominator -> verdict -> key -> delivered
```

| 선택 | 묻는 것 | 스킬이 받아들이지 않는 것 |
|---|---|---|
| **goal** (목표) | 도메인에서 쓰는 말로 "작업은 ___이고, 성공은 ___이다" | 해석에 따라 전혀 다른 계층이 나오는 모호한 목표 |
| **material** (자료) | 가진 자료 전부. 각각을 *키 후보*와 *원자료*로 나눔 | — |
| **denominator** (분모) | 셀 수 있는 두 집합의 곱. 그 안의 단위 하나하나가 처리 결과를 받아야 함 | 분모 자리에 들어온 표본("우리 파일 10,000개") |
| **verdict** (판정) | lens family마다 가장 강한 판정 수단, 그 등급(tier)과 소요 시간 | 사람이나 모델의 판단밖에 없는 family(finding이 아니라 lead만 냄) |
| **key** (키) | 다섯 가지 클래스 중 하나, 봉인 방식, 남은 수량, 학습 데이터 컷오프 | 키 자리에 들어온, 직접 고른 세트 |
| **delivered** (전달) | 결과를 받는 쪽이 정한 가장 엄격한 정의 | 전달 숫자를 부풀리고 손실을 감추는 느슨한 정의 |

스킬은 질문하기 전에 자료부터 읽고, 자료를 보고 알 수 있는 것은 묻지 않습니다. 막연한 질문 대신
선택지를 **제안**하며 선택지마다 무엇을 포기하게 되는지 밝힙니다. 답은 이유와 함께
`domains/<name>/INTERVIEW.md`에 남기므로, 나중에 설계를 다시 검토할 때 기억이 아니라 기록을 근거로
삼을 수 있습니다.

### 하드 게이트 세 개

| 게이트 | 통과 조건 |
|---|---|
| **0.1** 볼 수 없었던 키 | 시간이나 제3자가 봉인했고, 물리적으로 격리됨(에이전트에게 지시하는 게 아니라 파일 권한으로 막음) |
| **0.2** 채점 재현 가능 | 내가 관여하지 않은, 이미 알려진 결과를 스코어러가 똑같이 재현함 |
| **0.3** 기계적 판정 | 실제로 실행되는 메커니즘(테스트, 검사기, 정확 일치 스크립트)이고, 오케스트레이터가 직접 실행함 |
| 0.4 규모 산정 | 분모가 정해졌고, 완료 여부를 셀 수 있음 |

하드 게이트가 실패하면 다음 중 하나를 **사용자가** 고릅니다. **키 없는 프로그램**을 돌리거나,
**키를 직접 만들거나**, **중단**합니다. 키 없는 프로그램은 attrition, 손실 귀속, gate 종료 코드
규칙, 규칙 원장, 검증된 자가 보고로 이루어지며 어느 것도 recall은 측정하지 못합니다. 키는 과거
이력으로 재구성하거나 recall의 하한만 알려 주는 주입 방식으로 만듭니다. 설정을 계속 진행하려고
통과하지 못한 게이트를 통과로 체크하는 일은 절대 없습니다.

### 라운드

라운드 1이 할 일은 **천장 단계를 찾는 것** 하나뿐이고, 그동안 아무것도 바꾸지 않습니다. 그 뒤의
라운드는 다음 순서로 진행합니다.

1. `SEALED.md`에서 아직 쓰지 않은 대상을 하나 고르고, 아무것도 실행하기 전에 `PREREGISTRATION.md`를
   씁니다. 어떤 결과를 실패로 볼지도 여기에 적습니다.
2. 키를 작업 트리 밖으로 옮기고 대상을 읽기 전용으로 만듭니다.
3. `ROUND.md`의 항목을 하나씩 진행합니다. 에이전트가 스스로 보고한 내용은 모두 별도 도구로 확인하고
   라운드 도중 발견한 결함은 기록만 해 둡니다.
4. 키는 채점 항목에 와서야 엽니다. `compare.py`가 계층에 정해 둔 필드 규칙대로 답을 키와 하나씩
   비교하고 규칙으로 판단이 안 되는 필드는 판정 에이전트가 두 값만 보고 판정합니다. 실패 분석
   에이전트가 실패한 문제마다 유형, 단계, 원인을 붙이고, 빠짐없이 붙기 전까지 `failures.py`가 다음
   단계로 넘어가지 못하게 막습니다. 그다음 `score_round.py`로 두 축 점수와 단계별 손실 크기를
   계산하고 `ceiling.py`로 놓친 항목이 각각 어느 단계에서 떨어졌는지 확인합니다.
5. `RESULT.md`에 결과를 정리합니다. 찾은 것, 전달된 것, 단계별 손실, 천장, 그리고 **유지율**을
   적습니다. 유지율은 지난 라운드에서 맞힌 것 중 이번에도 맞힌 것을 가리킵니다.

다음 라운드에서는 천장 단계에서 고른 **한 가지**만 바꿉니다. 변경할 때는 학습 카드와 기계적 검사를
같은 커밋에 넣고 검사가 제대로 작동하는지는 사보타주로 확인합니다. 고친 버그를 일부러 되살렸을 때
검사가 실패해야 합니다.

---

## 하지 않는 일

- 분모, 판정, 키, 전달의 정의를 사용자 동의 없이 정하지 않습니다.
- 통과하지 못한 Phase 0 게이트를 체크하지 않습니다.
- `new_domain.py --check`가 통과시키지 않은 계층으로 라운드를 돌리지 않습니다.
- 라운드 도중에는 아무것도 고치지 않습니다.
- 키 없는 프로그램의 숫자를 recall이나 precision으로 보고하지 않습니다.
- 에이전트가 스스로 보고한 내용을 결과로 인정하지 않습니다.
- 채점 단계 전에는 키를 열지 않습니다.
- 프로젝트에 있는 파일을 덮어쓰지 않습니다.

---

## 설치되는 파일

```
<project>/
  CLAUDE.md                  loop rules L-1 … L-16, loaded into every session
  ORCHESTRATOR.md PLAN.md PHASE0.md ROUND.md STAGES.md
  SCORING.md CONTAMINATION.md VERIFY.md FAILURES.md     the kit's guidelines
  loop.config.yaml           copied from your layer once its gates are green
  scripts/                   gatelib + tools + your gate scripts
  harness/                   run_all.py · conformance/ (exit-code test) · <lesson>/ checks
  templates/                 PREREGISTRATION, RESULT, SEALED, RULE-LEDGER, card, gate, agents
  .claude/agents/            one agent per stage
  domains/<your-domain>/
    INTERVIEW.md             your six decisions, with reasons
    PHASE0-<instance>.md     the hard gates, and the decision if one failed
    SURFACE.md VERDICTS.md COMPARE.md STAGES.md loop.config.yaml
    lenses/*.md              directed question families
  references/learned/        one card per measured loss
  runs/<date>-<name>/        PREREGISTRATION.md ROUND.md census.json scored.json RESULT.md
  SEALED.md                  key inventory: what is left and what each round spent
```

### 가이드라인

| 파일 | 내용 |
|---|---|
| `CLAUDE.md` | 루프 규칙 L-1 … L-16. 규칙마다 그 규칙을 만든 측정값이 붙어 있음 |
| `ORCHESTRATOR.md` | 오케스트레이터가 할 일과 하면 안 되는 일, D-1 … D-8 |
| `PLAN.md` | 초기 구축 단계와 라운드 주기 |
| `PHASE0.md` | 루프를 적용할 수 있는지 판단하는 워크시트: 하드 게이트와, 0.1이 실패했을 때 할 일 |
| `ROUND.md` | 라운드 체크리스트. 라운드마다 하나씩 복사해 씀 |
| `STAGES.md` | 단계 명세의 일곱 필드와, 각 필드가 빠졌을 때 치른 비용 |
| `SCORING.md` | 키 클래스별 스코어러 구성(A 수정 이력 / B 판정 세트 / C 없음) |
| `CONTAMINATION.md` | 정답이 새어 들어갔을 때 라운드를 통째로 버리지 않고 단계별로 판정하는 법 |
| `VERIFY.md` | 에이전트의 자가 보고를 기계적으로 확인하는 방법 모음 |
| `FAILURES.md` | 실제로 측정된 실패 목록. 6개 유형별 비용과 현재 대책 |

---

## 도메인 계층

키트 자체는 특정 도메인에 묶여 있지 않습니다. 측정하며 개선하는 루프를 어떻게 돌리는지만 다루고,
무슨 작업인지는 다루지 않습니다. 키트를 특정 작업에 맞추는 것이 **도메인 계층**입니다. 보통은
스킬이 사용자와 함께 계층을 만들지만, 아래 명령으로 뼈대를 직접 만들 수도 있습니다.

```bash
python3 scripts/new_domain.py --name <domain> --instances <a> <b>
python3 scripts/new_domain.py --check domains/<domain>
```

계층은 일곱 가지 구성 요소로 이루어지고 하나라도 빠지면 라운드를 돌리지 못합니다.

| 구성 요소 | 답하는 질문 |
|---|---|
| `PHASE0-<instance>.md` | 이 도메인에서 루프를 돌릴 수 있는가? |
| `SURFACE.md` | 분모는 무엇인가? |
| `VERDICTS.md` | 우리 의견 없이 "이건 진짜다"라고 확인해 주는 수단은 무엇인가? |
| `COMPARE.md` | 답을 키와 어떻게 비교하고, 실패를 어떤 유형으로 나누는가? |
| `STAGES.md` | 어떤 단계가 있고, 각 단계의 명세는 무엇인가? |
| `lenses/` | 전체 대상(surface)에 어떤 방향성 있는 질문을 던지는가? |
| `loop.config.yaml` | 위 내용 전부를 기계가 읽을 수 있게 정리한 설정 |

다섯 도메인에서 같은 세 가지 선택을 해 보면 다음과 같습니다.

| 도메인 | 분모 | 가장 좋은 판정 | 키를 봉인하는 것 |
|---|---|---|---|
| 버그 수정 | 보고된 이슈 × 수정된 모듈 | 수정에 딸린 회귀 테스트가 수정 전에는 실패, 수정 후에는 통과 | 수정 이력, 시간 |
| 테스트 생성 | 공개 함수 × 문서화된 동작 | 테스트가 버그 있는 리비전에서 실패, 수정본에서 통과 | 수정 이력, 시간 |
| 문서 추출 | 스키마 필드 × 문서 | 게시된 값과 스크립트로 비교해 정확히 일치 | 컷오프 이후 제3자가 게시한 항목 |
| 예측 | 질문 × 결정일 | 실제 결과로 판정 | 실행 이후에 결정되는 질문 |
| 스펙 적합성 | 메시지 유형 × 필드 × 전이 | 실제 구현이 받아들이는 합성 메시지 | 나중에 공개된 명세 |

공통점이 있습니다. 분모는 모두 **셀 수 있는 두 집합의 곱**이고, 판정은 모두 **실제로 실행되는
메커니즘**이며, 키는 모두 **시간이나 제3자**가 봉인합니다. 세 답 중 이 모양에서 벗어난 것이 있다면
대개 더 약한 것으로 바뀌어 있습니다. 분모 자리에 표본이, 판정 자리에 의견이, 키 자리에 직접 고른
세트가 들어간 경우입니다.

---

## 도구와 종료 코드 규칙

모든 도구는 같은 종료 코드 규칙을 따릅니다(`scripts/gatelib.py`).

```
0 PASS    judged, and it passed
1 FAIL    judged, and it failed
2 CANNOT  could not judge — unreadable input, empty input, missing tool. NOT a pass.
3 USAGE   the invocation was wrong
```

앞에서 말한 과거 기록에서 가장 자주 반복된 결함은 문제를 출력해 놓고도 종료 코드 0으로 끝나는
gate였습니다. 여덟 번이나 일어났고 그때마다 따로 고쳤습니다. 그래서 gate 각자의 주의에 기대는
대신, 모든 gate를 한꺼번에 검사하는 conformance 테스트 하나로 이 규칙을 강제합니다.

| 도구 | 하는 일 |
|---|---|
| `scripts/loop_state.py` | 스킬이 다음에 실행할 단계를 출력 |
| `scripts/new_domain.py` | 도메인 계층의 뼈대를 만들거나 검사(채우지 않은 placeholder도 찾음) |
| `scripts/score_round.py` | 두 축으로 채점. 숫자 하나로 합치지 않고 어느 단계 탓인지 정해지지 않은 손실을 표시 |
| `scripts/ceiling.py` | 추론 대신 모든 산출물을 검색해서 천장 단계를 찾음 |
| `scripts/compare.py` | 답을 같은 문제의 키와 필드 규칙대로 비교해 `scored.json`에 기록 |
| `scripts/failures.py` | 실패한 문제마다 유형, 단계, 원인이 붙을 때까지 막고 유형별·단계별로 집계 |
| `scripts/attrition.py` | 후보 → 제출 → 전달 단계별 개수를 세고 탈락마다 원인을 기록. 키 없이도 동작 |
| `scripts/lint_cards.py` | 학습 카드에 특정 대상의 고유명사가 있으면 거부해서, 교훈을 다른 대상에도 쓸 수 있게 유지 |
| `harness/conformance/test_exit_codes.py` | 설정된 모든 gate가 규칙을 지키는지 세 가지 경우로 확인 |
| `harness/run_all.py` | conformance 테스트와 교훈별 검사(`harness/<lesson>/test_*.py`)를 모두 실행해 하나의 판정으로 보고 |

새 gate는 규칙을 이미 지키고 있는 `templates/gate.py`를 복사해서 만듭니다. `check()`를 바꾸고
`loop.config.yaml`에 등록한 뒤 conformance 테스트를 돌리면 됩니다.

에이전트 템플릿도 네 개 들어 있습니다. 두 개는 라운드마다 채점에 씁니다. `failure-analyst`는 라운드
산출물을 검색해 실패한 문제에 유형, 단계, 원인을 붙입니다. `answer-judge`는 규칙으로 판단이 안 되는
필드를 두 값만 보고 판정하며 비교 규칙에 `judge` 필드가 있을 때만 필요합니다. 나머지 두 개는 선택
사항입니다. 파이프라인에 전달 전 후보를 걸러 내는 단계가 있을 때만, 그 판단을 독립적으로 다시
검증하는 데 씁니다. `refuter`는 주장만 받고 추론 과정은 받지 않으며, `blind-rereader`는 결론 없이
위치만 받습니다.

**설치 확인.** 방금 설치한 프로젝트에는 입력이 없으므로, 모든 도구가 판정을 거부해야 합니다.

```bash
python3 harness/conformance/test_exit_codes.py              # 2
python3 scripts/lint_cards.py                               # 2
python3 scripts/attrition.py --round runs/nope              # 2
python3 scripts/ceiling.py --round runs/nope --missed x     # 2
python3 scripts/score_round.py --round runs/nope            # 2
python3 scripts/new_domain.py --check domains/nope          # 2
python3 scripts/loop_state.py                               # 0 -> phase setup:interview
```

이 중 하나라도 0으로 끝난다면 그 도구는 빈 입력을 성공으로 보고한 셈이고 실제 라운드에서도 똑같이
잘못된 성공을 보고합니다.

---

## 노력 배분 우선순위

규칙이 나온 그 라운드들에서 실제로 가치를 얻거나 잃은 지점을 중요한 순서대로 나열했습니다.

1. **전달 관리**(선별, 등급 매기기, 제출): 측정된 손실이 가장 컸습니다. 한 라운드에서 키 항목
   13개 중 9개를 찾았는데, 실제로 전달된 것은 2개뿐이었습니다.
2. **분모 커버리지**: 간단한 누락 검사만으로, 다 만들어 놓고 제출하지 않은 항목 15개를
   찾아냈습니다.
3. **두 메커니즘이 만나는 지점**: 두 부분은 각각 멀쩡한데, 맞물리는 곳에서만 결함이 생깁니다. 가장
   가치가 높은 결과가 여기서 나왔습니다.
4. **독립적인 재검증**: 블라인드 패스, 특히 결론을 전혀 보지 않고 다시 읽는 패스.
5. **탐지 범위 넓히기**: 가치가 가장 낮았습니다.

그런데도 사람들은 본능적으로 5번에 노력을 쏟습니다. 도메인에 이미 잘 만들어진 자동화 도구가 있다면
후보는 그 도구로 뽑고, 에이전트의 노력은 1–4번에 쓰세요.

---

## 기여

이슈와 PR은 언제든 환영합니다. 먼저 [CONTRIBUTING.md](CONTRIBUTING.md)를 읽어 주세요. 핵심만
말하면, 키트는 특정 도메인에 묶이지 않아야 하고(테스트로 강제), 모든 도구는 종료 코드 규칙을 지켜야
하며, 수정할 때는 원래 결함이 있으면 실패하는 테스트를 함께 넣어야 합니다.

```bash
pip install -r requirements.txt
python3 -m unittest discover -s tests -v
```

## 라이선스

[MIT](LICENSE)
