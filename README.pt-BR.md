# Equilibrium

🌐 **Idioma:** [English](README.md) | [Français](README.fr.md) | **Português** 

**Uma aplicação web multiusuário desenvolvida para auxiliar terapeutas holísticos, principalmente os que trabalham com aplicação de Reiki, na gestão de pacientes, agendamentos e sessões de terapia à distância.**

Equilibrium é um projeto de portfólio desenvolvido com **Python, Flask e MySQL**, criado para ajudar terapeutas a organizar sua rotina de trabalho enquanto oferece aos pacientes uma experiência dedicada para sessões remotas.

O projeto busca demonstrar não apenas funcionalidades, mas também preocupação com **segurança, isolamento de dados, manutenibilidade e reprodução do ambiente de instalação**.

> **Status:** Projeto de portfólio ativo
> **Demo online:** Em breve

---

## Visão geral

O Equilibrium foi criado para centralizar as principais atividades de um terapeuta em uma única aplicação.

Os terapeutas podem gerenciar pacientes e agendamentos, enquanto cada terapia agendada pode gerar uma sessão dedicada com música, cronômetro regressivo e um token de acesso exclusivo.

O sistema também possui ferramentas administrativas para gerenciamento de contas de terapeutas e permissões de acesso.

### Principais objetivos

* Centralizar o gerenciamento de pacientes
* Organizar agendamentos
* Disponibilizar uma experiência dedicada para sessões de terapia energética à distância
* Isolar os dados entre terapeutas
* Gerenciar o acesso dos terapeutas por meio de uma conta administrativa
* Aplicar medidas práticas de segurança à autenticação e aos formulários
* Manter o projeto simples de instalar e reproduzir localmente

---

## Funcionalidades

### Autenticação e controle de acesso

* Autenticação segura com hash de senha utilizando bcrypt
* Perfis `ADMIN` e `TERAPEUTA`
* Status de conta ativo/inativo
* Invalidação automática da sessão quando um usuário é desativado
* Validação das permissões atuais diretamente no banco de dados, sem depender apenas dos dados armazenados na sessão
* Rate limiting no login
* Proteção CSRF

### Administração de terapeutas

Administradores podem:

* Criar contas de terapeutas
* Editar informações de terapeutas
* Ativar ou desativar contas
* Redefinir senhas de terapeutas
* Acessar a listagem administrativa de usuários

Também existe um comando CLI para criar com segurança o **primeiro administrador** durante a configuração de uma nova instalação.

---

### Gerenciamento de pacientes

Terapeutas podem:

* Cadastrar pacientes
* Editar informações dos pacientes
* Armazenar dados de contato opcionais e observações
* Consultar pacientes com paginação

Os registros são isolados por meio de `terapeuta_id`, garantindo que cada terapeuta trabalhe apenas com seus próprios pacientes.

Os números de telefone são normalizados antes de serem armazenados. Assim, valores como:

```text id="zxbjvh"
(11) 99999-9999
11 9 9999 9999
11999999999
```

são tratados como o mesmo número.

O telefone é opcional e, quando informado, deve ser único **dentro da carteira de pacientes daquele terapeuta**.

---

### Gerenciamento de agendamentos

Terapeutas podem:

* Criar agendamentos
* Definir a duração da sessão
* Escolher a música da sessão
* Editar a data e o horário agendados
* Cancelar agendamentos
* Consultar o histórico com paginação
* Abrir a sessão de terapia vinculada ao agendamento

A interface também calcula o horário previsto de término com base no horário de início e na duração selecionada.

---

### Sessão de terapia

Cada agendamento pode gerar uma sessão de terapia dedicada.

A sessão inclui:

* Token de acesso exclusivo
* Duração configurável
* Cronômetro regressivo
* Música ambiente
* Imagens de fundo específicas para cada tema
* Persistência do estado da sessão após recarregar a página
* Encerramento automático da sessão
* Controles de reprodução de áudio

Os temas disponíveis incluem:

* 528Hz River
* Traditional
* Nature
* Ocean
* Spirit
* Cosmic

O cronômetro é calculado a partir dos timestamps da sessão registrados no servidor, evitando que um recarregamento da página reinicie uma sessão ativa.

---

### Dashboard

O dashboard do terapeuta apresenta uma visão geral da atividade, incluindo indicadores como:

* Pacientes cadastrados
* Agendamentos futuros
* Agendamentos concluídos
* Agendamentos cancelados
* Próximos agendamentos
* Pacientes recentes

---

## Tecnologias

### Backend

* Python
* Flask
* MySQL
* mysql-connector-python
* bcrypt
* python-dotenv

### Segurança

* Flask-WTF / CSRFProtect
* Flask-Limiter
* Hash de senhas com bcrypt
* Queries SQL parametrizadas
* Autenticação baseada em sessão
* Autorização baseada em perfil
* Isolamento de dados por terapeuta

### Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2

### Desenvolvimento e testes

* pytest
* Flask test client
* Mocking e monkeypatching
* Git / GitHub

---

## Arquitetura

O Equilibrium utiliza uma arquitetura Flask leve, com separação entre rotas HTTP e a camada de serviços responsável pela lógica de negócio e acesso aos dados.

```text id="8vtpzr"
Navegador
   │
   ▼
Rotas Flask
   │
   ▼
Camada de serviços
   │
   ▼
MySQL
```

Os templates e arquivos estáticos são organizados separadamente:

```text id="ps5tue"
Templates Jinja2
      │
      ├── base.html
      └── app_base.html
              │
              ├── Dashboard
              ├── Pacientes
              ├── Agendamentos
              └── Administração
```

A aplicação evita intencionalmente complexidade arquitetural desnecessária, mantendo uma separação clara de responsabilidades.

---

## Estrutura do projeto

```text id="4wk1ye"
equilibrium/
│
├── app/
│   ├── routes/
│   ├── services/
│   ├── static/
│   │   ├── css/
│   │   ├── img/
│   │   └── js/
│   ├── templates/
│   │   └── admin/
│   ├── utils/
│   ├── cli.py
│   ├── extensions.py
│   └── __init__.py
│
├── database/
│   ├── migrations/
│   └── schema.sql
│
├── tests/
│   ├── conftest.py
│   ├── test_access.py
│   ├── test_auth.py
│   └── test_cli.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
└── run.py
```

---

## Banco de dados

O repositório contém o schema completo do banco:

```text id="1uf9oa"
database/schema.sql
```

Isso permite que uma nova instalação recrie a estrutura necessária sem depender do banco utilizado durante o desenvolvimento.

As principais entidades são:

```text id="p3xxst"
usuarios
pacientes
agendamentos
sessoes
```

A propriedade de cada paciente é definida diretamente por `terapeuta_id`, garantindo isolamento dos dados entre terapeutas.

Alterações estruturais destinadas a instalações existentes são armazenadas em:

```text id="jksvjc"
database/migrations/
```

---

## Instalação

### 1. Clone o repositório

```bash id="fk7hg8"
git clone <repository-url>
cd equilibrium
```

---

### 2. Crie um ambiente virtual

```bash id="14l6qe"
python -m venv venv
```

Windows:

```powershell id="wnhq2i"
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash id="3h2e21"
source venv/bin/activate
```

---

### 3. Instale as dependências

```bash id="i95sld"
pip install -r requirements.txt
```

---

### 4. Crie o banco MySQL

```sql id="kysxkq"
CREATE DATABASE equilibrium
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Depois importe o schema:

```sql id="lq8mcp"
USE equilibrium;

source database/schema.sql;
```

---

### 5. Configure as variáveis de ambiente

Crie um arquivo `.env` com base em:

```text id="ldkg6h"
.env.example
```

Exemplo:

```env id="sekl9a"
SECRET_KEY=replace-with-a-secure-secret-key

DB_HOST=localhost
DB_USER=root
DB_PASS=your_mysql_password
DB_NAME=equilibrium
```

Você pode gerar uma chave secreta segura para o Flask com:

```bash id="pzvf3l"
python -c "import secrets; print(secrets.token_hex(32))"
```

Nunca faça commit do arquivo `.env` real.

---

### 6. Crie o primeiro administrador

Depois de configurar o banco:

```bash id="eh88o3"
python -m flask --app run.py create-admin
```

O comando solicitará:

```text id="9xv63t"
Nome
E-mail
Telefone
Senha
Confirmação da senha
```

A senha é armazenada de forma segura utilizando bcrypt.

Esse comando foi criado para inicializar uma nova instalação e impede a criação de outro administrador inicial caso já exista um.

---

### 7. Inicie a aplicação

```bash id="dxxmbr"
python run.py
```

A aplicação estará disponível localmente em:

```text id="cd88a7"
http://127.0.0.1:5000
```

Para desenvolvimento com debug:

```bash id="abp5ae"
python -m flask --app run.py run --debug
```

O modo debug não deve ser utilizado em produção.

---

## Health Check

O Equilibrium disponibiliza:

```text id="1ydu4k"
GET /health
```

Quando a aplicação e o banco estão disponíveis:

```json id="o4jgjc"
{
  "api": "online",
  "database": "online",
  "status": "ok"
}
```

Código HTTP:

```text id="flsc14"
200 OK
```

Caso a aplicação não consiga se conectar ao banco:

```text id="5diww4"
503 Service Unavailable
```

---

## Testes automatizados

Instale as dependências de desenvolvimento com:

```bash id="4iuyk3"
pip install -r requirements-dev.txt
```

Execute a suíte de testes:

```bash id="5hqfzn"
python -m pytest
```

A suíte atual está concentrada nas partes críticas e sensíveis à segurança da aplicação.

### Autenticação

Os testes cobrem:

* Usuários ativos com credenciais válidas
* Usuários inativos
* Senhas incorretas
* Usuários inexistentes
* Falhas de conexão com o banco

### Sessão e autorização

Os testes verificam que:

* Rotas protegidas recusam usuários não autenticados
* Usuários ativos acessam rotas protegidas
* Usuários desativados perdem sessões previamente autenticadas
* Terapeutas não acessam rotas administrativas
* Administradores acessam rotas administrativas
* Informações antigas de perfil armazenadas na sessão não sobrescrevem as permissões atuais do banco

### CLI

Os testes cobrem:

* Criação bem-sucedida do administrador inicial
* Impedimento da criação de múltiplos administradores iniciais
* Validação da senha
* Erros vindos da camada de serviços

Os testes utilizam mocks quando apropriado para validar as principais regras de autenticação e autorização sem depender de uma instância real do MySQL.

---

## Segurança

A segurança foi tratada como parte da arquitetura da aplicação, e não como uma melhoria posterior.

As medidas implementadas incluem:

* Hash de senhas com bcrypt
* Proteção CSRF
* Rate limiting no login
* Queries SQL parametrizadas
* Filtragem de dados por terapeuta
* Verificações de autorização no servidor
* Verificação de status da conta em requisições protegidas
* Invalidação de sessões de usuários desativados
* Credenciais e segredos armazenados em variáveis de ambiente
* Mensagens genéricas de falha na autenticação
* Tokens de acesso às sessões gerados de forma segura

Nenhuma credencial real é armazenada no repositório.

---

## Screenshots

### Dashboard

![Equilibrium dashboard](docs/screenshots/dashboard.png)

### Detalhes do dashboard

![Equilibrium dashboard](docs/screenshots/dashboard-details.png)

### Cadastro de pacientes

![Patient management](docs/screenshots/patients.png)

### Agenda

![Appointment management](docs/screenshots/appointments.png)

### Detalhes da agenda

![Appointment management details](docs/screenshots/appointments-details.png)

### Tela de sessão

![Therapy session](docs/screenshots/session.png)

### Administração de usuários

![Administration](docs/screenshots/admin.png)

---

## Assets de áudio

A sessão de terapia utiliza faixas de áudio originais geradas especificamente para o projeto Equilibrium utilizando o Suno em um plano pago.

Os arquivos de áudio são incluídos no projeto para permitir a reprodução completa da experiência da sessão em ambiente local.

**Os assets de áudio não fazem parte da licença de software deste repositório e não podem ser redistribuídos separadamente do projeto sem autorização.**

---

## Decisões de design

Algumas decisões importantes tomadas durante o desenvolvimento incluem:

### Autorização baseada no banco de dados

A sessão identifica o usuário autenticado, mas o status atual da conta e as permissões são validados diretamente no banco.

Isso impede que dados antigos da sessão mantenham acesso após a desativação de uma conta ou alteração de perfil.

### Integridade garantida pelo banco

Constraints importantes, como a unicidade do telefone do paciente dentro da carteira de um terapeuta, são aplicadas diretamente no banco de dados.

A camada de serviços traduz erros técnicos de integridade em mensagens compreensíveis para o usuário.

### Armazenamento canônico de telefones

Os números de telefone são normalizados antes de serem armazenados, em vez de manter caracteres de formatação.

Isso permite que a apresentação visual seja alterada sem modificar o valor persistido.

### Arquitetura leve

O projeto utiliza intencionalmente uma arquitetura Flask simples e clara, evitando adicionar repositories, ORMs ou camadas arquiteturais sem necessidade.

O objetivo é manter boa manutenibilidade e separação de responsabilidades sem over-engineering.

---

## Roadmap

Possíveis melhorias futuras incluem:

* Autenticação de dois fatores para administradores
* Logging mais avançado em produção
* Armazenamento externo para rate limiting em ambientes distribuídos
* Maior cobertura de testes automatizados
* Melhorias de acessibilidade
* Relatórios e análises mais detalhados
* Monitoramento do deploy

---

## Autor

**Antonio Silos**

Desenvolvedor de software com foco em backend, APIs, bancos de dados e aplicações web práticas.

---

## Licença
O código-fonte do Equilibrium está licenciado sob a Licença MIT. Veja LICENSE para mais detalhes.
Os arquivos de áudio localizados em app/sound/ estão excluídos da Licença MIT e estão sujeitos a restrições de uso separadas. Veja AUDIO_ASSETS_NOTICE.md.
