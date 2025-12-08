---
sidebar_position: 0
---

# 비디오 가이드

FluxLoop VSCode Extension의 주요 기능을 영상과 함께 빠르게 살펴보세요.

---

## 1. Projects

FluxLoop 프로젝트를 생성하는 두 가지 방법입니다.

### Default 모드 (권장)

<iframe
  width="100%"
  height="400"
  src="https://www.youtube.com/embed/vyzmJWKLHHg"
  title="FluxLoop - Default Mode Project Creation"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

**Default 모드**는 현재 열려있는 워크스페이스를 에이전트 소스로 재사용합니다. 환경을 자동으로 감지하고, FluxLoop 설정 파일들은 공유 루트 폴더(`~/FluxLoopProjects`)에 생성됩니다.

- 대부분의 사용자에게 권장되는 방식
- 기존 프로젝트 구조를 변경하지 않음
- 빠른 시작 가능

### Custom 모드 (고급)

<iframe
  width="100%"
  height="400"
  src="https://www.youtube.com/embed/VIDEO_ID_CUSTOM_MODE"
  title="FluxLoop - Custom Mode Project Creation"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

**Custom 모드**는 프로젝트 위치와 설정을 완전히 제어하고 싶을 때 사용합니다.

- 모노레포, 원격 폴더 등 복잡한 구조에 적합
- FluxLoop 설정을 소스 트리 내부에 배치 가능
- 세밀한 환경 설정 지원

:::warning Environment 선택 시 주의사항
두 모드 모두 프로젝트 생성 과정에서 **Python 환경을 선택**하는 단계가 있습니다.

**실제 에이전트가 실행되는 가상환경(venv, Conda 등)이 있다면 반드시 해당 환경을 선택하세요.** 그렇지 않으면 시스템 기본 Python이 선택되며, 에이전트에 필요한 패키지들이 설치되어 있지 않아 실험 실행 시 오류가 발생할 수 있습니다.
:::

---

## 2. Environment

Python 환경 설정 및 상태 확인 방법입니다.

### System Console

<iframe
  width="100%"
  height="400"
  src="https://www.youtube.com/embed/VIDEO_ID_ENVIRONMENT"
  title="FluxLoop - Environment Setup"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

- **Select Environment**: 프로젝트에서 사용할 Python 인터프리터를 선택합니다. venv, Conda, Poetry, pyenv, uv 등 다양한 환경을 자동으로 감지합니다.
- **Show Environment**: 현재 선택된 환경의 상세 정보(Python 버전, 설치된 패키지 등)를 확인합니다.

---

## 3. Inputs

에이전트 테스트를 위한 입력 데이터를 생성합니다.

### Generate New Inputs

<iframe
  width="100%"
  height="400"
  src="https://www.youtube.com/embed/VIDEO_ID_INPUTS"
  title="FluxLoop - Generate Inputs"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

입력 생성 전에 **Base Input 설정이 필요합니다**. `configs/input.yaml` 파일에서 페르소나와 기본 입력값을 정의한 후, Generate 기능을 사용하여 다양한 변형 입력을 자동 생성할 수 있습니다.

---

## 4. Experiments

시뮬레이션을 준비하고 실험을 실행합니다.

### Prepare Simulation

<iframe
  width="100%"
  height="400"
  src="https://www.youtube.com/embed/VIDEO_ID_PREPARE_SIM"
  title="FluxLoop - Prepare Simulation"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

:::info 참고
Prepare Simulation은 설정 가이드일 뿐입니다. 실제 실험을 위해서는 직접 셋업이 필요합니다:

- [FluxLoop SDK 기본 사용법](/sdk/getting-started/basic-usage) - 에이전트 코드에 SDK 적용하기
- [Runner 설정 가이드](/cli/configuration/runner-targets) - 다양한 Runner 패턴 (Python, HTTP, Subprocess 등)
- [pytest 통합](/cli/workflows/pytest-integration) - CI/CD 파이프라인에서 실험 실행하기
:::

### Run Experiment

<iframe
  width="100%"
  height="400"
  src="https://www.youtube.com/embed/VIDEO_ID_RUN_EXPERIMENT"
  title="FluxLoop - Run Experiment"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

준비된 시뮬레이션 설정을 바탕으로 실험을 실행합니다. 실행 중인 실험의 진행 상황을 실시간으로 확인할 수 있습니다.

:::tip 복잡한 Args 설정이 어렵다면?
시뮬레이션에 필요한 `args` 설정이 복잡하거나 어렵다면, [Recording Mode](./recording-mode)를 활용해보세요. 실제 에이전트 실행 시 사용된 인자를 녹화해두고, 이후 실험에서 그대로 재사용할 수 있습니다.
:::

---

## 5. Evaluation

실험 결과를 분석하고 평가합니다.

<iframe
  width="100%"
  height="400"
  src="https://www.youtube.com/embed/VIDEO_ID_EVALUATION"
  title="FluxLoop - Evaluation"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

평가는 세 단계로 진행됩니다:

1. **Configure**: 평가 기준과 메트릭을 설정합니다.
2. **Parse**: 실험 결과에서 평가에 필요한 데이터를 추출합니다.
3. **Evaluate**: 설정된 기준에 따라 결과를 평가하고 점수를 산출합니다.

---

## 다음 단계

각 기능에 대한 자세한 설명은 아래 문서를 참고하세요:

- [프로젝트 생성](./creating-projects) - 상세 프로젝트 설정 가이드
- [환경 설정](./environment-setup) - Python 환경 구성
- [입력 관리](./managing-inputs) - 입력 데이터 생성 및 관리
- [실험 실행](./running-experiments) - 시뮬레이션 실행 방법
- [결과 확인](./viewing-results) - 실험 결과 분석
