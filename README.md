# Number Guess API

Aplikacja webowa/API napisana w Pythonie z użyciem FastAPI. Projekt prezentuje kompletny proces DevOps: testowanie, konteneryzację, skanowanie bezpieczeństwa, publikowanie obrazu Docker, automatyczne wdrażanie na AWS oraz zarządzanie infrastrukturą przy użyciu Terraform.

## Linki

- Repozytorium: https://github.com/Raz0er/number-guess-api
- Obraz Docker Hub: https://hub.docker.com/r/razoer/number-guess-api
- Publiczny adres aplikacji: `http://<PUBLIC_IP>`

Publiczny adres aplikacji można odczytać po utworzeniu infrastruktury:

```bash
terraform -chdir=terraform output -raw public_url
```

Adres IP może się zmienić po usunięciu i ponownym utworzeniu instancji EC2.

---

## Opis aplikacji

Number Guess API to gra polegająca na odgadnięciu liczby losowanej z zakresu od 1 do 100.

Aplikacja udostępnia:

- prosty interfejs webowy,
- endpoint sprawdzający stan aplikacji,
- endpoint zwracający wersję i commit wdrożenia,
- endpoint biznesowy do zgadywania liczby,
- możliwość zresetowania gry,
- dokumentację Swagger UI.

Stan gry jest przechowywany w pamięci aplikacji. Restart kontenera powoduje rozpoczęcie nowej gry.

---

## Endpointy

### `GET /`

Wyświetla interfejs webowy gry.

### `GET /health`

Sprawdza stan aplikacji.

Przykładowa odpowiedź:

```json
{
  "status": "ok",
  "timestamp": "2026-07-14T16:36:18.727712+00:00"
}
```

### `GET /version`

Zwraca wersję aplikacji i skrócony identyfikator commita Git.

```json
{
  "version": "v1.0.17",
  "commit": "2431153"
}
```

Wartości `APP_VERSION` i `APP_COMMIT` są przekazywane podczas budowania obrazu Docker i zapisywane również jako etykiety OCI.

### `POST /guess`

Endpoint biznesowy służący do zgadywania liczby.

```bash
curl -X POST http://<PUBLIC_IP>/guess \
  -H "Content-Type: application/json" \
  -d '{"number": 50}'
```

Przykładowa odpowiedź:

```json
{
  "result": "too_low",
  "message": "Za mało.",
  "attempts": 1
}
```

Możliwe wyniki:

- `too_low`,
- `too_high`,
- `correct`.

### Reset gry

Reset wykonuje się przez nagłówek `X-Reset-Game`:

```bash
curl -X POST http://<PUBLIC_IP>/guess \
  -H "X-Reset-Game: true"
```

Odpowiedź:

```json
{
  "result": "reset",
  "message": "Gra została zresetowana. Wylosowano nową liczbę.",
  "attempts": 0
}
```
### Dokumentacja API

FastAPI automatycznie udostępnia Swagger UI:

```text
http://<PUBLIC_IP>/docs
```

---

## Architektura

```text
Developer
    |
    | git push
    v
GitHub
    |
    v
GitHub Actions
    |
    +--> Pytest
    +--> Docker Buildx
    +--> Trivy
    +--> Docker Hub
    |
    +--> GitHub OIDC
             |
             v
          AWS IAM
             |
             v
     AWS Systems Manager
             |
             v
         Amazon EC2
             |
             v
      Docker / FastAPI
             |
             v
     CloudWatch Logs
```

Terraform odpowiada za utworzenie infrastruktury AWS, natomiast GitHub Actions realizuje proces CI/CD i wdrożenie nowej wersji aplikacji.

---

## Struktura repozytorium

```text
number-guess-api/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── __init__.py
│   └── main.py
├── terraform/
│   ├── cloudwatch.tf
│   ├── ec2.tf
│   ├── iam.tf
│   ├── network.tf
│   ├── oidc.tf
│   ├── outputs.tf
│   ├── provider.tf
│   ├── security.tf
│   ├── terraform.tfvars.example
│   ├── user_data.sh.tftpl
│   ├── variables.tf
│   └── versions.tf
├── tests/
│   └── test_number.py
├── .dockerignore
├── .gitignore
├── Dockerfile
├── pytest.ini
├── requirements.txt
├── requirements-test.txt
└── README.md
```

---

## Uruchomienie lokalne

### Python

Utworzenie środowiska wirtualnego:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instalacja zależności:

```bash
python -m pip install --upgrade pip
pip install -r requirements-test.txt
```

Uruchomienie aplikacji:

```bash
uvicorn app.main:app --reload
```

Aplikacja będzie dostępna pod adresem:

```text
http://127.0.0.1:8000
```

### Testy

```bash
pytest -v
```

Testy obejmują:

- `/health`,
- `/version`,
- interfejs webowy,
- zgadywanie liczby,
- walidację danych,
- reset gry,
- licznik prób.

---

## Docker

### Budowa obrazu

```bash
docker build \
  --build-arg APP_VERSION=local \
  --build-arg APP_COMMIT="$(git rev-parse --short HEAD)" \
  -t number-guess-api:local .
```

### Uruchomienie kontenera

```bash
docker run --rm \
  --name number-guess-api \
  -p 8000:8000 \
  number-guess-api:local
```

Sprawdzenie aplikacji:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/version
```

Dockerfile zawiera również `HEALTHCHECK`, który cyklicznie sprawdza endpoint `/health`.
Aplikacja w kontenerze działa jako nieuprzywilejowany użytkownik `appuser` z UID `10001`, zamiast jako użytkownik `root`.

---

## Infrastructure as Code

Infrastruktura jest zarządzana za pomocą Terraform.

Tworzone zasoby:

- VPC,
- publiczna podsieć,
- Internet Gateway,
- routing,
- Security Group,
- instancja EC2 z Amazon Linux 2023,
- role i polityki IAM,
- profil instancji,
- grupa logów CloudWatch,
- rola GitHub Actions używana przez OIDC.

Instancja EC2:

- posiada szyfrowany dysk EBS GP3,
- wymaga IMDSv2,
- nie posiada AWS Key Pair,
- nie ma otwartego portu SSH,
- jest zarządzana przez AWS Systems Manager.

Publicznie otwarty jest wyłącznie port:

```text
TCP 80
```

### Uruchomienie Terraform

```bash
terraform -chdir=terraform init
terraform -chdir=terraform fmt -check
terraform -chdir=terraform validate
terraform -chdir=terraform plan
terraform -chdir=terraform apply
```

Odczyt adresu aplikacji:

```bash
terraform -chdir=terraform output -raw public_url
```

Usunięcie infrastruktury:

```bash
terraform -chdir=terraform destroy
```

Stan Terraform jest przechowywany lokalnie i nie jest publikowany w repozytorium.

Nie należy usuwać pliku `terraform.tfstate` przed wykonaniem `terraform destroy`, ponieważ Terraform wykorzystuje go do identyfikowania zarządzanych zasobów.



Wymaganie OIDC

Na koncie AWS musi być wcześniej skonfigurowany dostawca GitHub OIDC:

https://token.actions.githubusercontent.com

Umożliwia on GitHub Actions uzyskanie krótkotrwałych poświadczeń AWS bez przechowywania stałych kluczy dostępowych. Terraform wykorzystuje istniejącego dostawcę OIDC do utworzenia roli IAM używanej podczas wdrażania aplikacji.

Instrukcja konfiguracji:

https://github.com/aws-actions/configure-aws-credentials#oidc-configuration-details

### Połączenie z instancją przez AWS Systems Manager

Instancja EC2 jest zarządzana przez AWS Systems Manager Session Manager, dlatego nie wymaga otwartego portu SSH ani klucza prywatnego.

Pobranie identyfikatora instancji:

terraform -chdir=terraform output -raw instance_id

Uruchomienie sesji:

aws ssm start-session --region eu-central-1 --target "$(terraform -chdir=terraform output -raw instance_id)"

Po zakończeniu pracy sesję można zamknąć poleceniem:

exit

---

## CI/CD

Pipeline znajduje się w:

```text
.github/workflows/ci.yml
```

Uruchamia się po:

- pushu do `main`,
- utworzeniu Pull Requesta do `main`,
- ręcznym uruchomieniu przez `workflow_dispatch`.

### Pull Request

```text
testy -> build obrazu -> skan Trivy
```

Obraz nie jest publikowany, a aplikacja nie jest wdrażana.

### Push do `main`

```text
test -> docker -> deploy -> tag_release
```

Pipeline:

1. Instaluje zależności i uruchamia testy pytest.
2. Generuje wersję w formacie v1.0.<GITHUB_RUN_NUMBER>.
3. Buduje obraz Docker.
4. Skanuje obraz narzędziem Trivy.
5. Zatrzymuje pipeline, jeśli Trivy wykryje podatność HIGH lub CRITICAL, dla której dostępna jest poprawka.
6. Publikuje obraz w Docker Hub.
7. Uzyskuje tymczasowe poświadczenia AWS przez GitHub OIDC.
8. Wdraża nową wersję aplikacji na EC2 przez AWS Systems Manager.
9. Sprawdza poprawność wdrożenia za pomocą endpointów /health i /version.
10. Po poprawnym wdrożeniu tworzy anotowany tag Git.

Obraz otrzymuje trzy tagi:

```text
latest
v1.0.<GITHUB_RUN_NUMBER>
<pełny SHA commita>
```

---

## Konfiguracja GitHub Actions

### Repository Variables

```text
DOCKERHUB_USERNAME
AWS_REGION
AWS_ROLE_ARN
```

Przykład:

```text
DOCKERHUB_USERNAME=razoer
AWS_REGION=eu-central-1
AWS_ROLE_ARN=arn:aws:iam::<ACCOUNT_ID>:role/number-guess-api-github-actions-role
```

### Repository Secrets

```text
DOCKERHUB_TOKEN
```

Token Docker Hub powinien posiadać tylko uprawnienia potrzebne do publikowania obrazu.

Stałe klucze AWS nie są przechowywane w GitHub. Uwierzytelnianie odbywa się przez krótkotrwałe poświadczenia OIDC.

---

## Logi i monitoring

Endpoint zdrowia:

```text
GET /health
```

Jest wykorzystywany przez:

- Docker `HEALTHCHECK`,
- GitHub Actions smoke test,
- ręczną diagnostykę aplikacji.

Logi kontenera są wysyłane do grupy CloudWatch:

```text
/number-guess-api/application
```

Podgląd logów:

```bash
aws logs tail /number-guess-api/application \
  --region eu-central-1 \
  --follow
```

Każde wdrożenie używa strumienia logów zawierającego skrócony commit Git, co pozwala przypisać logi do konkretnej wersji aplikacji.

---

## Bezpieczeństwo

W projekcie zastosowano:

- GitHub OIDC zamiast stałych kluczy AWS,
- ograniczone polityki IAM,
- wdrażanie i administrację przez AWS Systems Manager,
- zamknięty port SSH,
- wymagane IMDSv2,
- szyfrowany dysk EBS,
- token Docker Hub zapisany jako GitHub Secret,
- skanowanie obrazu przez Trivy,
- Docker `HEALTHCHECK`,
- smoke testy po wdrożeniu,
- tworzenie taga Git dopiero po poprawnym deploymentcie.
- uruchamianie aplikacji w kontenerze jako nieuprzywilejowany użytkownik `appuser`,

Aplikacja działa obecnie przez HTTP. W środowisku produkcyjnym należałoby zastosować domenę, certyfikat TLS oraz HTTPS.

## Autor

Krzysztof Rosłon

Projekt zaliczeniowy na kierunku DevOps – Administrator infrastruktury IT.
