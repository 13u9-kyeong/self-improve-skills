# selfimprove

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Claude Code skill](https://img.shields.io/badge/Claude%20Code-skill%20%2B%20plugin-8A63D2.svg)

**어떤 도메인이든, 에이전트 파이프라인에 *측정되는* 자가개선 루프를 만들어 주는 Claude Code
스킬입니다. 사용자와 인터뷰하며 채점 계층과 게이트를 만들고, 채점되는 라운드를 돌립니다.**

[English README](README.md)

```
/selfimprove "an agent that extracts fields from supplier invoices, built from our AP archive"
```

대부분의 에이전트 파이프라인은 누군가 결과물을 다시 읽어 보고 나아졌다고 느끼는 방식으로
"개선"됩니다. 이 스킬은 그것을 허용하지 않습니다. 라운드는 **누구도 반박할 수 없는 방식으로 틀릴
수 있을 때만** 의미가 있고, 그러려면 세 가지가 필요합니다.

1. **파이프라인이 볼 수 없었던 키.** 시간이나 제3자가 봉인한 것이어야 하며, 직접 골라 둔 홀드아웃
   세트여서는 안 됩니다.
2. **도메인 고유의 통화로 채점하는 스코어러.** 항상 두 숫자를 하나로 합치지 않고 보고합니다:
   *찾은 것*과 *전달된 것*.
3. **실행 전에 써 둔 기록.** 어떤 결과가 불리하게 해석되는지를 미리 적어 둡니다.

스킬은 이것들을 한 번에 한 결정씩 사용자와 함께 만듭니다. 그다음 라운드를 돌려 지표의 천장이
결정되는 단 하나의 단계를 찾아내고, 라운드마다 한 가지만 바꿉니다. 도메인에 그런 키가 없다면 스킬은
그렇다고 말하며, 점수를 지어내지 않습니다.

---

## 목차

- [설치](#설치)
- [빠른 시작](#빠른-시작)
- [세션 한 번의 처음부터 끝까지](#세션-한-번의-처음부터-끝까지)
- [동작 방식](#동작-방식)
- [절대 하지 않는 것](#절대-하지-않는-것)
- [프로젝트에 추가되는 것](#프로젝트에-추가되는-것)
- [도메인 계층](#도메인-계층)
- [도구와 종료 코드 규칙](#도구와-종료-코드-규칙)
- [노력을 어디에 쓸 것인가](#노력을-어디에-쓸-것인가)
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

플러그인 스킬은 네임스페이스가 붙으므로 **`/selfimprove:selfimprove`**로 호출합니다. 특정
릴리스에 고정하려면 저장소 URL 뒤에 `#v1.0.0`을 붙이세요. 저장소가 GitHub 비공개 저장소이므로
`/plugin`보다 먼저 `git`이 이 저장소를 clone할 수 있어야 합니다(예: `gh auth login` 후
`gh auth setup-git`).

### 단독 스킬로 설치

```bash
git clone https://github.com/13u9-kyeong/self-improve-skills.git
self-improve-skills/install.sh              # all projects -> ~/.claude/skills/selfimprove/
self-improve-skills/install.sh --project    # this project -> ./.claude/skills/selfimprove/
```

**`/selfimprove`**로 호출합니다. 업데이트할 때는 pull한 뒤 `install.sh`를 다시 실행하세요. 설치본이
통째로 교체됩니다.

어느 방식이든 스킬 디렉터리의 `kit/`에 키트 전체가 들어 있습니다. 어떤 프로젝트에서 스킬을 처음
호출하면, 그 프로젝트에 키트를 설치하기 전에 먼저 묻습니다. 파일은 절대 덮어쓰지 않습니다. 프로젝트에
이미 `CLAUDE.md`가 있으면 루프 규칙을 `# Self-improvement loop` 제목 아래에 덧붙이고 diff를
보여 줍니다.

---

## 빠른 시작

1. 에이전트가 일할 프로젝트에서 Claude Code를 엽니다.
2. 원하는 것을 한 문장으로 말합니다: `/selfimprove "X를 하는 에이전트, Y 기반으로"`.
3. 여섯 가지 질문에 답합니다. 질문마다 구체적인 선택지가 2–4개 나오고, 추천안이 맨 앞에 있으며,
   각 선택지가 무엇을 측정 불가능하게 만드는지 적혀 있습니다.
4. 계층과 게이트를 만들게 둔 다음, 라운드를 더 돌리고 싶을 때마다 "다음 라운드 돌려"라고 말합니다.

언제든 멈춰도 됩니다. 다음 주에 `/selfimprove`를 다시 호출하면 답하지 않은 첫 질문, 또는 체크되지
않은 첫 항목부터 이어서 진행합니다.

**이럴 때 쓰세요.** 반복되는 작업에서 에이전트가 측정 가능하게 나아지기를 원할 때. 예를 들면:

- 변경 이력이 공개된 코드베이스에서 버그 수정이나 테스트 작성
- 문서에서 구조화된 데이터 추출, 분류, 라벨링
- 예측, 데이터 분석, 포맷이나 프로토콜의 스펙 적합성 작업
- 그 밖에 무엇이 "완료"이고 무엇이 "증거"인지 말할 수 있는 모든 작업

**이럴 때는 쓰지 마세요.** 일회성 작업. 반복해서 채점되는 라운드가 없으면 루프가 개선할 대상이
없습니다.

---

## 세션 한 번의 처음부터 끝까지

도메인은 예시이고 답변도 지어낸 것이지만, 흐름은 스킬이 실제로 하는 그대로입니다. (아래 기록은
영문판과 같게 유지하기 위해 원문 그대로 둡니다.)

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

에이전트가 처음 보는 문제를 풉니다. 각 답은 미리 정해 둔 규칙에 따라 같은 문제에 대한 키의 답, 즉
과거 보고서나 정답지와 비교됩니다. 실패마다 이유를 붙이고, 천장 단계에서 가장 많이 나온 이유를 고친
뒤, 다음 라운드는 새로운 문제로 돌립니다.

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

### 스킬은 자기 단계를 추측하지 않습니다

호출될 때마다 `scripts/loop_state.py`를 실행합니다. 이 스크립트가 프로젝트 파일을 읽고 실행할
단계를 출력합니다. 이 규칙들이 나온 이력에서 오케스트레이터의 실패는 모두 같은 모양이었습니다.
오케스트레이터가 파일이 어떻게 보이는지를 보고 자기 단계를 추측한 것입니다.

| 단계 | 진입 조건 | 하는 일 |
|---|---|---|
| `setup:interview` | `INTERVIEW.md`가 없거나, 답하지 않은 선택이 남음 | 사용자와 여섯 가지 결정, 기록 |
| `setup:phase0` | 인터뷰 완료, 체크되지 않은 하드 게이트가 있고 결정 기록이 없음 | 하드 게이트 세 개, 하나가 실패하면 사용자가 결정 |
| `setup:layer` | Phase 0 결정됨, `new_domain.py --check`가 아직 계층을 거부 | surface, verdicts, stages, 에이전트, lenses, config |
| `setup:gates` | 계층 완성, 설정된 gate 중 스크립트가 없는 것이 있음 | gate 스크립트, conformance 테스트, 사보타주 검사 |
| `round:baseline` | 모두 만들어짐, 채점된 라운드 없음 | 라운드 1: 천장을 찾고, 아무것도 바꾸지 않음 |
| `round:in-progress` | `ROUND.md`는 있고 `RESULT.md`는 없는 라운드가 있음 | 체크되지 않은 첫 항목부터 재개 |
| `round:next` | 채점된 라운드가 하나 이상 | 천장 단계에서 고른 변경 하나, 그다음 라운드 |

### 여섯 가지 결정은 사용자와 함께 내립니다

```
goal -> material -> denominator -> verdict -> key -> delivered
```

| 선택 | 묻는 것 | 스킬이 반대하는 것 |
|---|---|---|
| **goal** (목표) | 도메인 자체의 말로 "작업은 ___이고, 성공은 ___이다" | 서로 다른 계층을 만들게 되는 해석 |
| **material** (자료) | 가진 것 전부, 각 부분을 *키 후보* 또는 *원자료*로 표시 | — |
| **denominator** (분모) | 열거 가능한 두 집합의 곱. 그 각 단위가 처리 결과를 받아야 함 | 분모 대신 내놓은 표본("우리 파일 10,000개") |
| **verdict** (판정) | lens family마다 가장 강한 메커니즘, 그 등급(tier)과 소요 시간 | 판단밖에 없는 family: finding이 아니라 lead만 냄 |
| **key** (키) | 다섯 가지 클래스 중 하나, 봉인 방식, 재고, 학습 데이터 컷오프 | 키 대신 내놓은 직접 고른 세트 |
| **delivered** (전달) | 목적지가 제공하는 가장 엄격한 정의 | 전달 숫자를 부풀리고 손실을 감추는 느슨한 정의 |

스킬은 무엇이든 묻기 전에 자료부터 읽습니다. 보고 알아낼 수 있는 것은 묻지 않습니다. 질문은
열린 질문 대신 선택지를 **제안**하고, 각 선택지는 무엇을 포기하는지 밝힙니다. 답은 이유와 함께
`domains/<name>/INTERVIEW.md`에 기록되므로, 나중에 설계를 기억이 아니라 기록을 근거로 다시 따질 수
있습니다.

### 하드 게이트 세 개

| 게이트 | 통과 조건 |
|---|---|
| **0.1** 볼 수 없었던 키 | 시간이나 제3자가 봉인했고, 물리적으로 격리됨(에이전트에게 주는 지시가 아니라 파일 권한) |
| **0.2** 채점 재현 가능 | 스코어러가 내가 관여하지 않은 알려진 결과를 재현함 |
| **0.3** 판정이 기계적 | 실행되는 메커니즘(테스트, 검사기, 정확 일치 스크립트)이고, 오케스트레이터가 직접 실행함 |
| 0.4 크기 산정 | 분모가 정해졌고, 완료 여부를 셀 수 있음 |

하드 게이트가 실패하면 **사용자가** 고릅니다. **키 없는 프로그램**을 돌리거나(attrition, 손실 귀속,
gate 종료 코드 규칙, 규칙 원장, 검증된 자가 보고. 이 중 어느 것도 recall을 측정하지 않음), **키를 구성하거나**
(과거 이력으로 재구성, 또는 recall의 하한만 주는 주입), **중단**합니다. 스킬은 설정을 계속하려고
통과하지 못한 게이트를 체크하는 일이 절대 없습니다.

### 라운드

라운드 1의 일은 하나입니다. **천장 단계를 찾는 것.** 그동안 아무것도 바꾸지 않습니다. 이후 각
라운드는:

1. `SEALED.md`에서 쓰지 않은 대상을 하나 고르고, 무엇이든 실행하기 전에 `PREREGISTRATION.md`를
   씁니다. 결과가 불리하게 해석되는 조건도 포함합니다.
2. 키를 작업 트리 밖으로 옮기고 대상을 읽기 전용으로 만듭니다.
3. `ROUND.md`를 한 칸씩 진행하면서 에이전트의 자가 보고를 모두 다른 도구로 확인하고, 결함은
   라운드 도중에 고치지 않고 기록만 합니다.
4. 채점 칸에서만 키를 엽니다. `compare.py`가 계층의 필드 규칙대로 각 답을 키와 비교하고, 규칙으로
   정할 수 없는 필드는 블라인드 판정 에이전트가 맡습니다. 실패 분석 에이전트가 실패한 문제마다
   유형, 단계, 원인을 붙이고, 모두 붙을 때까지 `failures.py`가 막습니다. 그다음 `score_round.py`(두
   축, 단계별 손실 가격)와 `ceiling.py`(각 누락이 어디서 죽었는지)를 실행합니다.
5. `RESULT.md`를 씁니다: 찾은 것, 전달된 것, 단계별 손실, 천장, 그리고 **유지율**(지난 라운드의
   적중 중 몇 개가 살아남았는지).

다음 라운드는 천장 단계에서 고른 **한 가지**만 바꿉니다. 변경은 학습 카드와 기계적 검사를 한
커밋에 담아 내보내고, 검사는 사보타주로 검증합니다. 버그를 되살려 검사가 빨간불이 되는지
확인하는 것입니다.

---

## 절대 하지 않는 것

- 분모, 판정, 키, 전달의 정의를 사용자 없이 정하지 않습니다.
- 통과하지 못한 Phase 0 게이트를 체크하지 않습니다.
- `new_domain.py --check`가 거부하는 계층에서 라운드를 돌리지 않습니다.
- 라운드 도중에 무엇도 고치지 않습니다.
- 키 없는 프로그램의 숫자를 recall이나 precision으로 보고하지 않습니다.
- 에이전트의 자가 보고를 결과로 취급하지 않습니다.
- 채점 단계 전에 키를 열지 않습니다.
- 프로젝트의 파일을 덮어쓰지 않습니다.

---

## 프로젝트에 추가되는 것

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
| `CLAUDE.md` | 루프 규칙 L-1 … L-16, 각 규칙을 만든 측정값과 함께 |
| `ORCHESTRATOR.md` | 조정 에이전트의 의무와 금지 사항, D-1 … D-8 |
| `PLAN.md` | 부트스트랩 단계와 라운드별 주기 |
| `PHASE0.md` | 적용 가능성 워크시트: 하드 게이트, 그리고 0.1이 실패할 때 할 일 |
| `ROUND.md` | 라운드별 체크리스트, 라운드마다 한 부씩 |
| `STAGES.md` | 단계 명세: 일곱 필드, 그리고 각 필드가 없을 때 치른 비용 |
| `SCORING.md` | 키 클래스별 스코어러 구성(A 수정 이력 / B 판정 세트 / C 없음) |
| `CONTAMINATION.md` | 라운드를 버리지 않고 유출을 단계별로 판정하는 법 |
| `VERIFY.md` | 자가 보고를 기계적으로 확인하는 방법 모음 |
| `FAILURES.md` | 측정된 실패 목록: 6개 클래스, 각각의 비용과 현재 방어책 |

---

## 도메인 계층

키트는 도메인과 무관합니다. 측정되는 루프가 어떻게 돌아가는지만 말하고, 작업이 무엇인지는 말하지
않습니다. **도메인 계층**이 키트를 한 종류의 작업에 적용합니다. 보통은 스킬이 사용자와 함께 계층을
만들지만, 직접 뼈대를 만들 수도 있습니다.

```bash
python3 scripts/new_domain.py --name <domain> --instances <a> <b>
python3 scripts/new_domain.py --check domains/<domain>
```

계층은 일곱 구성 요소로 이루어지며, 하나라도 빠지면 라운드가 돌지 않습니다.

| 구성 요소 | 답하는 질문 |
|---|---|
| `PHASE0-<instance>.md` | 여기서 루프를 돌릴 수 있기는 한가? |
| `SURFACE.md` | 분모는 무엇인가? |
| `VERDICTS.md` | 우리 의견에 기대지 않고 "이것은 진짜다"라고 말해 주는 것은 무엇인가? |
| `COMPARE.md` | 답 하나를 키와 어떻게 비교하고, 실패를 각각 무엇이라 부르는가? |
| `STAGES.md` | 어떤 단계들이, 어떤 명세 아래 있는가? |
| `lenses/` | 전체 surface에 걸쳐 어떤 지향 질문들을 돌리는가? |
| `loop.config.yaml` | 위의 모든 것을 기계가 읽을 수 있는 형태로 |

같은 세 가지 선택을 다섯 도메인에 대해 그려 보면:

| 도메인 | 분모 | 가장 좋은 판정 | 키를 봉인하는 것 |
|---|---|---|---|
| 버그 수정 | 보고된 이슈 × 수정된 모듈 | 수정의 회귀 테스트가 전에는 실패, 후에는 통과 | 수정 이력, 시간 |
| 테스트 생성 | 공개 함수 × 문서화된 동작 | 테스트가 버그 있는 리비전에서 실패, 수정본에서 통과 | 수정 이력, 시간 |
| 문서 추출 | 스키마 필드 × 문서 | 게시된 값과 스크립트로 정확히 일치 | 컷오프 이후 제3자가 게시한 항목 |
| 예측 | 질문 × 결정일 | 실현된 결과로 판정 | 실행 이후에 결정되는 질문 |
| 스펙 적합성 | 메시지 유형 × 필드 × 전이 | 실제 구현이 받아들이는 합성 메시지 | 나중에 공개된 명세 |

공통점은 이렇습니다. 모든 분모는 **열거 가능한 두 집합의 곱**이고, 모든 판정은 **실행되는
메커니즘**이며, 모든 키는 **시간이나 제3자**가 봉인합니다. 세 답이 이런 모양이 아니라면 대개 하나가
더 약한 것으로 바뀌어 있습니다. 분모 대신 표본, 판정 대신 의견, 키 대신 직접 고른 세트.

---

## 도구와 종료 코드 규칙

모든 도구는 하나의 규칙을 지킵니다(`scripts/gatelib.py`).

```
0 PASS    judged, and it passed
1 FAIL    judged, and it failed
2 CANNOT  could not judge — unreadable input, empty input, missing tool. NOT a pass.
3 USAGE   the invocation was wrong
```

문제를 출력하고도 0으로 끝나는 gate가, 이 규칙들이 나온 이력에서 가장 많이 반복된 결함이었습니다.
여덟 번 일어났고 매번 따로 고쳐졌습니다. 그래서 이 규칙은 gate마다 조심하는 방식이 아니라, 모든
gate를 대상으로 하는 conformance 테스트 하나로 강제합니다.

| 도구 | 하는 일 |
|---|---|
| `scripts/loop_state.py` | 스킬이 다음에 실행할 단계를 출력 |
| `scripts/new_domain.py` | 도메인 계층의 뼈대를 만들거나 검사(남은 placeholder 포함) |
| `scripts/score_round.py` | 두 축 스코어러. 숫자 하나로 합치기를 거부하고, 단계에 귀속되지 않은 손실을 표시 |
| `scripts/ceiling.py` | 추론이 아니라 모든 산출물을 검색해서 천장 단계를 찾음 |
| `scripts/compare.py` | 각 답을 같은 문제에 대한 키의 답과 필드 규칙대로 비교하고 `scored.json`을 씀 |
| `scripts/failures.py` | 실패한 문제마다 실패 유형, 단계, 원인이 붙을 때까지 막고, 유형별·단계별로 집계 |
| `scripts/attrition.py` | 후보 → 제출 → 전달 집계, 모든 탈락에 원인 기록. 키가 필요 없음 |
| `scripts/lint_cards.py` | 학습 카드에 든 대상의 고유명사를 거부해 교훈을 일반적으로 유지 |
| `harness/conformance/test_exit_codes.py` | 설정된 모든 gate에 대해 세 축으로 규칙을 확인 |
| `harness/run_all.py` | conformance 테스트와 모든 교훈별 검사(`harness/<lesson>/test_*.py`)를 하나의 판정으로 실행 |

새 gate는 이미 규칙을 지키는 `templates/gate.py`에서 시작합니다. 복사하고, `check()`를 바꾸고,
`loop.config.yaml`에 등록한 뒤, conformance 테스트를 돌리면 됩니다.

키트는 에이전트 템플릿 네 개도 함께 제공합니다. 두 개는 매 라운드 채점을 맡습니다:
`failure-analyst`(실패한 문제 하나에 라운드 산출물을 검색해 유형, 단계, 원인을 붙임)와
`answer-judge`(규칙으로 정할 수 없는 필드를 두 값만 보고 판정. 비교에 `judge` 필드가 있을 때만
필요). 나머지 두 개는 후보를 전달 전에 걸러 내는 단계가 있는 파이프라인에서만 쓰는 선택 적대적
패스입니다: `refuter`(주장만 받고 추론은 절대 받지 않음)와 `blind-rereader`(결론 없이 위치만 받음).

**설치 확인.** 갓 설치한 프로젝트에서는 모든 도구가 빈 입력에 대해 판정을 거부해야 합니다.

```bash
python3 harness/conformance/test_exit_codes.py              # 2
python3 scripts/lint_cards.py                               # 2
python3 scripts/attrition.py --round runs/nope              # 2
python3 scripts/ceiling.py --round runs/nope --missed x     # 2
python3 scripts/score_round.py --round runs/nope            # 2
python3 scripts/new_domain.py --check domains/nope          # 2
python3 scripts/loop_state.py                               # 0 -> phase setup:interview
```

이 중 하나라도 0으로 끝나면, 그 도구는 빈 입력에 성공을 보고하는 것이고, 실제 라운드에서도 같은
방식으로 성공을 보고할 것입니다.

---

## 노력을 어디에 쓸 것인가

이 규칙들이 나온 라운드에서 가치가 실제로 얻어지고 잃어진 곳의 순위입니다.

1. **전달 규율**: 선별, 등급 매기기, 제출. 측정된 손실 중 가장 컸습니다. 한 라운드에서 키 항목
   13개 중 9개를 찾았지만 전달된 것은 2개뿐이었습니다.
2. **분모의 커버리지**: 값싼 완전성 검사로, 끝내 놓고 한 번도 제출하지 않은 항목 15개를
   잡아냈습니다.
3. **두 메커니즘 사이의 상호작용**: 각각은 올바른 두 부분이 만나는 곳에만 존재하는 결함. 가장 가치
   높은 결과들이 여기서 나왔습니다.
4. **독립적인 재공격**: 블라인드 패스, 특히 결론을 전혀 보지 않는 패스.
5. **탐지 폭 자체**: 가치가 가장 적습니다.

노력은 본능적으로 5번으로 흘러갑니다. 도메인에 이미 성숙한 기계적 도구가 있다면 그 도구로 후보를
만들고, 에이전트의 노력은 1–4번에 쓰세요.

---

## 기여

이슈와 머지 요청을 환영합니다. 먼저 [CONTRIBUTING.md](CONTRIBUTING.md)를 읽어 주세요. 요약하면:
키트는 도메인 중립을 유지하고(테스트가 강제), 모든 도구는 종료 코드 규칙을 지키며, 모든 수정에는
원래 결함에서 실패하는 테스트가 함께 들어갑니다.

```bash
pip install -r requirements.txt
python3 -m unittest discover -s tests -v
```

## 라이선스

[MIT](LICENSE)
