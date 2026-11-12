# WxConvertor

App Android: escolhe o ZIP do resource pack (Minecraft Java ou Bedrock) e devolve **somente** o `.zip` do Blockman GO (sem o relatório `.json`; o `items.json` do atlas continua dentro do ZIP porque o jogo precisa dele).

O conversor é o próprio `mc_to_blockman.py`, rodando dentro do app via Chaquopy 16 (Python 3.11 + Pillow; 3.11 é a última versão com suporte a ARM 32 bits).

## Gerar o APK (sem PC)
1. Crie um repositório no GitHub e suba todo o conteúdo desta pasta.
2. Aba **Actions** > **Build APK** (roda sozinho a cada push).
3. Baixe o APK em **Artifacts** (`WxConvertor-apk`) e instale.

## Gerar no PC
Android Studio: abrir a pasta > Build > Build APK. Ou: `gradle :app:assembleDebug` (Gradle 8.7, JDK 17).

## Limitação conhecida
Som de hit em `.ogg`/`.wav` precisa de ffmpeg, que não existe no app: vai para `incompativeis`. `.mp3` é copiado normalmente.

## Ícone
Troque o arquivo `app/src/main/res/drawable-nodpi/ic_launcher.png` pelo seu PNG (quadrado, de preferência 512x512), mantendo o mesmo nome.
