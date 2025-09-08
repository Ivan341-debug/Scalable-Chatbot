# Vamos criar o arquivo README.md com o conteúdo estruturado que foi montado

readme_content = """# Chatbot com RabbitMQ, Redis, Whisper e PostgreSQL

Este projeto implementa um chatbot robusto, integrado com **Evolution API**, utilizando filas assíncronas para processamento de texto e áudio.  
O objetivo é garantir **escala, confiabilidade e persistência de histórico**, separando responsabilidades em diferentes workers.

---

## 🚀 Funcionalidades

- ✅ Processamento de mensagens de **texto** e **áudio** recebidas via Evolution API  
- ✅ Estrutura de filas com **RabbitMQ** para desacoplamento e escalabilidade  
- ✅ Conversão de áudios (base64 → arquivo temporário → texto via Whisper)  
- ✅ Cache de mensagens concatenadas e histórico em **Redis**  
- ✅ Armazenamento assíncrono do histórico em **PostgreSQL**  
- ✅ Resposta ao usuário processada por IA com contexto de conversas anteriores  
- ✅ Fluxo resiliente e modular com workers independentes  

---

## 🔄 Fluxo do Código

### 1. Recebimento das mensagens
- O **payload** vindo da **Evolution API** é tratado e enviado para filas no RabbitMQ:
  - **Fila de texto**
  - **Fila de áudio**

---

### 2. Processamento de Texto
- O **worker de texto**:
  - Inicia um **timer de 15 segundos** reiniciado a cada nova mensagem recebida dentro do intervalo.  
  - Durante esse tempo, as mensagens são concatenadas.  
  - O conteúdo concatenado é armazenado em **cache no Redis**.  
  - Após o timer, o texto concatenado é enviado para outra fila, destinada à IA.  

---

### 3. Processamento de Áudio
- O **worker de áudio**:
  - Recebe a mensagem em **base64**.  
  - Converte para um **arquivo temporário**.  
  - Utiliza o **Whisper** para transcrição do áudio em texto.  
  - Remove o arquivo temporário após a transcrição.  
  - Envia o texto transcrito para a fila da IA.  

---

### 4. Processamento da IA
- O **worker da IA**:
  - Consome a fila com mensagens concatenadas (texto ou transcrições de áudio).  
  - Gera a resposta para o usuário, considerando o **histórico em cache (Redis)**.  
  - Salva o histórico no Redis.  
  - Envia o histórico para uma **fila de persistência**.  

---

### 5. Persistência de Histórico
- O **worker de persistência**:
  - Consome a fila de histórico.  
  - Transcreve o conteúdo armazenado no Redis para o **PostgreSQL** de forma assíncrona.  

---

### 6. Resposta ao Usuário
- Após a IA processar a resposta:
  - A mensagem é enviada para a **fila response**.  
  - O worker de response envia o output ao usuário via **API da Evolution**.  

---

## 🛠️ Tecnologias Utilizadas

- **Python / Asyncio** – workers e processamento assíncrono  
- **RabbitMQ** – filas e orquestração de mensagens  
- **Redis** – cache de mensagens e histórico recente  
- **PostgreSQL** – persistência definitiva do histórico  
- **Whisper** – transcrição de áudio para texto  
- **Evolution API** – recebimento e envio de mensagens  

---

## 📌 Estrutura de Workers

- `worker_text` → processa mensagens de texto, concatena e envia para a IA  
- `worker_audio` → processa áudios, transcreve com Whisper e envia para a IA  
- `worker_ia` → consome mensagens, gera resposta com histórico e envia saída  
- `worker_persistencia` → grava o histórico do Redis no PostgreSQL  
- `worker_response` → envia a resposta final ao usuário via Evolution API  

---

## ⚡ Fluxo Resumido

```mermaid
flowchart TD
    A[Evolution API] --> B[Fila Texto]
    A --> C[Fila Áudio]

    B --> D[Worker Texto]
    C --> E[Worker Áudio]

    D --> F[Redis Cache]
    E --> F

    F --> G[Fila IA]
    G --> H[Worker IA]

    H --> I[Redis Histórico]
    I --> J[Fila Persistência]
    J --> K[PostgreSQL]

    H --> L[Fila Response]
    L --> M[Evolution API]
