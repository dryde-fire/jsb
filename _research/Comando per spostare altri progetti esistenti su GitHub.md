**Comando per spostare altri progetti esistenti su GitHub in `C:\Users\Sandro\Dev\`:**

```powershell
# Clona un progetto da GitHub (metodo consigliato per repos già su GitHub)
git clone https://github.com/dryde-fire/NOME-REPO.git C:\Users\Sandro\Dev\NOME-REPO
cd C:\Users\Sandro\Dev\NOME-REPO
npm install   # se è un progetto Node.js
```

**Se invece hai una cartella locale da spostare (come abbiamo fatto ora):**

```powershell
# 1. Copia (escludi node_modules e output)
robocopy "PERCORSO\ORIGINE" "C:\Users\Sandro\Dev\NOME-PROGETTO" /E /XD node_modules output /XF *.png

# 2. Installa dipendenze nel nuovo posto
cd C:\Users\Sandro\Dev\NOME-PROGETTO
npm install

# 3. Verifica che git punti ancora a GitHub
git remote -v
```

**Flusso di lavoro da più dispositivi (una volta spostato tutto in `Dev\`):**

```powershell
# Inizio sessione: scarica ultimi aggiornamenti
git pull

# Fine sessione: salva e carica
git add .
git commit -m "descrizione"
git push
```