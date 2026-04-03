const screen = document.getElementById("screen");

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const randomInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
const sample = (arr, count) => [...arr].sort(() => Math.random() - 0.5).slice(0, count);

const allAgents = [
  "Irene Quiralte", "Maksim Volkov", "Padma Rao", "Salvador Urrutia",
  "Amina Djebar", "Tomás Bellido", "Luca Ferrer", "Mireya Cifuentes"
];

const events = [
  {
    id: "puerto_fantasma",
    name: "Operación Puerto Fantasma",
    desc: "Entras al almacén del muelle 14. Néstor Cline dice que hay un microfilm, pero huele a trampa.",
    options: [
      ["Asaltar ya con equipo pesado", { fondos: -12, seguridad: +8, sospecha: +12, intel: +14 }],
      ["Sobornar al estibador Vela para entrar sin ruido", { fondos: -18, sospecha: -5, intel: +9, influencia: +4 }],
      ["Dejarlo correr y vigilar 48h", { seguridad: -6, intel: +4, sospecha: -2, delay: [2, { intel: +12, sospecha: +7 }] }]
    ]
  },
  {
    id: "cena_diplomatica",
    name: "Cena en Embajada Nival",
    desc: "Te sientas junto al ministro Oskar Venn. Sonríe como quien ya vendió tu funeral.",
    options: [
      ["Filtrar un rumor falso para medir fugas", { intel: +10, sospecha: +9, delay: [2, { seguridad: +6 }] }],
      ["Pagar al maître para cambiar su copa", { fondos: -10, influencia: +7, sospecha: +4, intel: +6 }],
      ["Callarte y observar", { influencia: -4, sospecha: -3, intel: +3, flag: "guardaste_silencio_sobre_ministro" }]
    ]
  },
  {
    id: "tren_orfeo",
    name: "Tren Orfeo a las 03:10",
    desc: "Lena Arce te mira por el reflejo de una cuchara. No sabes si está asustada o vendida.",
    options: [
      ["Extraer a Lena por fuerza", { seguridad: +5, fondos: -15, intel: +7, flag: "rescataste_lena", delay: [3, { intel: +14 }] }],
      ["Seguirla sin intervenir", { intel: +11, sospecha: +8, delay: [2, { seguridad: -8 }] }],
      ["Filtrar su ubicación a la prensa", { influencia: -8, sospecha: -7, fondos: +8, intel: -6 }]
    ]
  },
  {
    id: "subasta_negra",
    name: "Subasta Negra de Tallin",
    desc: "Te infiltras en una subasta donde venden el prototipo Asterión.",
    options: [
      ["Comprar el prototipo", { fondos: -25, seguridad: +12, intel: +6 }],
      ["Robarlo durante el apagón", { seguridad: -10, sospecha: +14, intel: +10 }],
      ["Vender tus planos viejos por liquidez", { fondos: +20, influencia: -8, flag: "vendiste_prototipo", delay: [3, { seguridad: -10, sospecha: +10 }] }]
    ]
  },
  {
    id: "cloaca_digital",
    name: "Cloaca Digital",
    desc: "Úrsula Brea te ofrece acceso al servidor enemigo si quemas su expediente.",
    options: [
      ["Aceptar trato con Úrsula", { intel: +15, sospecha: +6, flag: "quemaste_archivo_ursula", delay: [2, { influencia: +8 }] }],
      ["Detener a Úrsula y copiar su disco", { seguridad: +8, intel: +5, sospecha: +5, influencia: -4 }],
      ["Ignorarla y reforzar firewall", { seguridad: +4, intel: -3, sospecha: -2 }]
    ]
  },
  {
    id: "frontera_muda",
    name: "Frontera Muda",
    desc: "Entras en un puesto fronterizo con papeles falsos. Un capitán te reconoce.",
    options: [
      ["Activar bloqueo total de comunicaciones", { seguridad: +14, influencia: -9, fondos: -8, flag: "activaste_bloqueo_total" }],
      ["Negociar paso con contrabandista Jarek", { fondos: -6, intel: +10, flag: "pacto_con_mafia", delay: [2, { sospecha: +10, fondos: +10 }] }],
      ["Retirada táctica con señuelos", { seguridad: -4, sospecha: -4, intel: +6 }]
    ]
  },
  {
    id: "auditoria",
    name: "Auditoría Interna Fantasma",
    desc: "Llegan inspectores con sonrisas fotocopiadas. Quieren cuentas y nombres.",
    options: [
      ["Abrir libros reales", { fondos: -5, sospecha: -10, influencia: -5 }],
      ["Fabricar contabilidad creativa", { fondos: +10, sospecha: +11, delay: [2, { influencia: -9 }] }],
      ["Invitar inspectores a una misión de campo", { seguridad: +6, influencia: +5, fondos: -8, sospecha: +3 }]
    ]
  },
  {
    id: "catedral_humo",
    name: "La Catedral de Humo",
    desc: "El Círculo Sal te ofrece un nombre... a cambio de otro.",
    options: [
      ["Entregar un agente menor", { intel: +12, influencia: -10, sospecha: +5 }],
      ["Rechazar trato y plantar micro", { seguridad: +7, intel: +6, fondos: -7 }],
      ["Dar nombre falso de alto rango", { intel: +9, sospecha: +9, delay: [3, { seguridad: -12 }] }]
    ]
  },
  {
    id: "hospital_nocturno",
    name: "Hospital de Noche San Telmo",
    desc: "Un agente en coma susurra 'M.V.'. El doctor Soria pide dinero o silencio.",
    options: [
      ["Pagar tratamiento completo", { fondos: -16, intel: +8, seguridad: +4 }],
      ["Trasladar al agente a base secreta", { seguridad: +8, sospecha: +6, fondos: -6 }],
      ["Cortar soporte y extraer datos", { intel: +14, sospecha: +12, influencia: -7 }]
    ]
  }
];

const game = {
  state: "start",
  players: ["Operaciones (J1)", "Contrainteligencia (J2)"],
  maxDay: 12,
  timerRef: null,

  reset() {
    this.seed = randomInt(10000, 99999);
    this.day = 1;
    this.fondos = 70;
    this.influencia = 40;
    this.seguridad = 65;
    this.sospecha = 15;
    this.intel = 15;
    this.stress = 10;
    this.objetivos = 0;
    this.controlOwner = 0;
    this.choiceP1 = null;
    this.choiceP2 = null;
    this.resolveCursor = 0;
    this.timer = 12;
    this.currentEvent = null;
    this.currentOptions = [];
    this.discovered = new Set();
    this.doubleAgents = new Set(sample(allAgents, 2));
    this.delayedEffects = [];
    this.history = [];
    this.flags = {};
    this.finalTitle = "";
    this.finalText = "";
    this.stopTimer();
  },

  startEvent() {
    this.currentEvent = events[randomInt(0, events.length - 1)];
    this.currentOptions = this.currentEvent.options;
    this.choiceP1 = null;
    this.choiceP2 = null;
    this.resolveCursor = 0;
    this.timer = Math.max(5.5, 12 - (this.day - 1) * 0.5);
    this.state = "event";
    this.startTimer();
    render();
  },

  startTimer() {
    this.stopTimer();
    this.timerRef = setInterval(() => {
      if (this.state !== "event") return;
      this.timer = Math.max(0, this.timer - 0.1);
      if (this.timer === 0) {
        this.resolveChoices();
      }
      render();
    }, 100);
  },

  stopTimer() {
    if (this.timerRef) {
      clearInterval(this.timerRef);
      this.timerRef = null;
    }
  },

  buildFlavorText(label, effects) {
    const lines = [`Decides: ${label}.`];
    if ((effects.sospecha || 0) > 0) lines.push("Notas cámaras nuevas. También te están cazando.");
    if ((effects.seguridad || 0) < 0) lines.push("Tu red tiembla y dos claves maestras dejan de responder.");
    if ((effects.fondos || 0) < -12) lines.push("El tesorero jura en voz baja al ver la factura.");
    if ((effects.intel || 0) >= 10) lines.push("El rompecabezas encaja... y no te gusta la imagen final.");
    return lines.join(" ");
  },

  applyEffect(optionIndex, source = "manual") {
    const [label, effects] = this.currentOptions[optionIndex];
    this.fondos += effects.fondos || 0;
    this.influencia += effects.influencia || 0;
    this.seguridad += effects.seguridad || 0;
    this.sospecha += effects.sospecha || 0;
    this.intel += effects.intel || 0;
    this.stress += randomInt(1, 4);

    if (effects.flag) this.flags[effects.flag] = true;
    if (effects.delay) {
      const [rounds, delayed] = effects.delay;
      this.delayedEffects.push([this.day + rounds, delayed, label]);
    }

    this.history.push({
      day: this.day,
      event: this.currentEvent.name,
      choice: label,
      source,
      flavor: this.buildFlavorText(label, effects)
    });

    this.fondos = clamp(this.fondos, -20, 130);
    this.influencia = clamp(this.influencia, 0, 120);
    this.seguridad = clamp(this.seguridad, 0, 120);
    this.sospecha = clamp(this.sospecha, 0, 140);
    this.intel = clamp(this.intel, 0, 140);
    this.stress = clamp(this.stress, 0, 120);

    if (this.intel >= 85) this.objetivos = Math.max(this.objetivos, 3);
    else if (this.intel >= 55) this.objetivos = Math.max(this.objetivos, 2);
    else if (this.intel >= 30) this.objetivos = Math.max(this.objetivos, 1);

    this.tryDiscoverDoubleAgent();
  },

  tryDiscoverDoubleAgent() {
    const chance = 0.08 + this.intel / 250 + this.sospecha / 500;
    if (Math.random() < chance) {
      const unknown = [...this.doubleAgents].filter((a) => !this.discovered.has(a));
      if (unknown.length) {
        const found = unknown[randomInt(0, unknown.length - 1)];
        this.discovered.add(found);
        this.seguridad += 5;
        this.sospecha += 3;
        this.history.push({
          day: this.day,
          event: "Filtración interceptada",
          choice: "Nombre revelado",
          source: "intel",
          flavor: `Tu analista cifra una llamada y pronuncia un nombre: ${found}.`
        });
      }
    }
  },

  applyDelayedEffects() {
    const pending = [];
    for (const [targetDay, delayed, origin] of this.delayedEffects) {
      if (targetDay <= this.day) {
        this.fondos += delayed.fondos || 0;
        this.influencia += delayed.influencia || 0;
        this.seguridad += delayed.seguridad || 0;
        this.sospecha += delayed.sospecha || 0;
        this.intel += delayed.intel || 0;
        this.history.push({
          day: this.day,
          event: "Consecuencia diferida",
          choice: origin,
          source: "delay",
          flavor: `Efecto tardío aplicado por ${origin}.`
        });
      } else {
        pending.push([targetDay, delayed, origin]);
      }
    }
    this.delayedEffects = pending;
  },

  resolveChoices() {
    this.stopTimer();
    if (this.choiceP1 === null) this.choiceP1 = randomInt(0, 2);
    if (this.choiceP2 === null) this.choiceP2 = randomInt(0, 2);

    if (this.choiceP1 === this.choiceP2) {
      this.applyEffect(this.choiceP1, "consenso");
      this.state = "feedback";
      render();
      return;
    }

    this.state = "resolve";
    render();
  },

  lossReason() {
    if (this.seguridad <= 0) return "Tu red cae en una madrugada. Puertas abiertas y archivos vacíos.";
    if (this.fondos <= 0) return "Te quedas sin fondos. Los leales se marchan por mejores sueldos.";
    if (this.sospecha >= 100) return "Tu tapadera colapsa. Tu cara sale en portada antes del café.";
    if (this.stress >= 100) return "El mando se fragmenta. Ninguna orden llega intacta.";
    return null;
  },

  computeEnding() {
    const traitorScore = this.discovered.size;
    const win = this.day > this.maxDay && this.objetivos >= 3 && this.seguridad > 10 && this.fondos > 10;

    if (win && traitorScore >= 2) {
      this.finalTitle = "FINAL: Monarca de Sombras";
      this.finalText = "Sobrevives 12 rondas, expones a ambos dobles agentes y negocias desde fuerza.";
    } else if (win) {
      this.finalTitle = "FINAL: Victoria Hueca";
      this.finalText = "Sostienes la agencia a duras penas. Ganas en público, pero no en silencio.";
    } else if (this.sospecha >= 100) {
      this.finalTitle = "FINAL: Portada Roja";
      this.finalText = "El enemigo no necesita balas cuando tiene tus errores en horario estelar.";
    } else if (this.fondos <= 0) {
      this.finalTitle = "FINAL: Quiebra Patriótica";
      this.finalText = "Defiendes al país con pagarés y una cafetera empeñada.";
    } else if (this.seguridad <= 0) {
      this.finalTitle = "FINAL: Casa Abierta";
      this.finalText = "Tu edificio sigue en pie, pero ya no es tuyo.";
    } else {
      this.finalTitle = "FINAL: Cenizas Operativas";
      this.finalText = "No logras cerrar la operación. Quedan cabos sueltos y una silla vacía.";
    }
  },

  continueFromFeedback() {
    this.applyDelayedEffects();
    const reason = this.lossReason();
    if (reason) {
      this.computeEnding();
      this.finalText = `${reason} ${this.finalText}`;
      this.state = "end";
      render();
      return;
    }

    this.day += 1;
    this.controlOwner = 1 - this.controlOwner;
    if (this.day > this.maxDay) {
      this.computeEnding();
      this.state = "end";
      render();
      return;
    }
    this.startEvent();
  }
};

function statsBlock() {
  const found = game.discovered.size ? [...game.discovered].sort().join(", ") : "Ninguno confirmado";
  return `
    <div class="small">Día ${game.day}/${game.maxDay} · Semilla ${game.seed}</div>
    <div class="stats">
      <div class="stat"><div class="k">Fondos</div><div class="v">${game.fondos}</div></div>
      <div class="stat"><div class="k">Influencia</div><div class="v">${game.influencia}</div></div>
      <div class="stat"><div class="k">Seguridad</div><div class="v">${game.seguridad}</div></div>
      <div class="stat"><div class="k">Sospecha</div><div class="v">${game.sospecha}</div></div>
      <div class="stat"><div class="k">Intel</div><div class="v">${game.intel}</div></div>
      <div class="stat"><div class="k">Estrés</div><div class="v">${game.stress}</div></div>
      <div class="stat"><div class="k">Objetivos</div><div class="v">${game.objetivos}/3</div></div>
    </div>
    <div class="info">Mando actual: <strong>${game.players[game.controlOwner]}</strong> · Dobles detectados: ${found}</div>
  `;
}

function renderStart() {
  screen.innerHTML = `
    ${statsBlock()}
    <h2 class="state-title">Inicio</h2>
    <p class="event-desc">Proteges un país que no sabrá tu nombre. Sospechas que dos agentes trabajan para el enemigo.</p>
    <p class="event-desc">Controles: J1 vota con <kbd>1</kbd><kbd>2</kbd><kbd>3</kbd>; J2 con <kbd>J</kbd><kbd>K</kbd><kbd>L</kbd>. También puedes usar botones táctiles.</p>
    <div class="actions"><button id="startBtn" class="primary">Empezar partida</button></div>
  `;
  document.getElementById("startBtn").onclick = () => game.startEvent();
}

function renderEvent() {
  const timerClass = game.timer < 4 ? "timer danger" : "timer";
  screen.innerHTML = `
    ${statsBlock()}
    <h2 class="state-title">Operación activa</h2>
    <div class="event-name">${game.currentEvent.name}</div>
    <p class="event-desc">${game.currentEvent.desc}</p>
    <div class="${timerClass}">Tiempo restante: ${game.timer.toFixed(1)}s</div>

    <div class="options">
      ${game.currentOptions.map(([label], i) => `
        <article class="option">
          <div><strong>Opción ${i + 1}:</strong> ${label}</div>
          <div class="vote-row">
            <button data-vote="p1" data-index="${i}">J1 vota ${i + 1}</button>
            <button data-vote="p2" data-index="${i}">J2 vota ${i + 1}</button>
          </div>
        </article>
      `).join("")}
    </div>

    <div class="info">Votos actuales · J1: ${game.choiceP1 === null ? "-" : game.choiceP1 + 1} · J2: ${game.choiceP2 === null ? "-" : game.choiceP2 + 1}</div>
    <div class="actions"><button id="confirmVotes" class="primary" ${game.choiceP1 === null || game.choiceP2 === null ? "disabled" : ""}>Confirmar votos</button></div>
  `;

  screen.querySelectorAll("button[data-vote]").forEach((btn) => {
    btn.onclick = () => {
      const slot = btn.dataset.vote;
      const idx = Number(btn.dataset.index);
      if (slot === "p1") game.choiceP1 = idx;
      else game.choiceP2 = idx;
      render();
    };
  });

  document.getElementById("confirmVotes").onclick = () => game.resolveChoices();
}

function renderResolve() {
  const p1Text = game.currentOptions[game.choiceP1][0];
  const p2Text = game.currentOptions[game.choiceP2][0];
  screen.innerHTML = `
    ${statsBlock()}
    <h2 class="state-title">Votos en conflicto</h2>
    <p class="event-desc">${game.players[game.controlOwner]} decide el plan final.</p>
    <div class="options">
      <article class="option"><strong>Voto J1</strong><div>${p1Text}</div><button id="pickLeft">Elegir J1</button></article>
      <article class="option"><strong>Voto J2</strong><div>${p2Text}</div><button id="pickRight">Elegir J2</button></article>
    </div>
    <p class="small">Atajo teclado: <kbd>←</kbd> y <kbd>→</kbd> para marcar, <kbd>Enter</kbd> para confirmar.</p>
  `;

  document.getElementById("pickLeft").onclick = () => {
    game.applyEffect(game.choiceP1, "mando");
    game.state = "feedback";
    render();
  };
  document.getElementById("pickRight").onclick = () => {
    game.applyEffect(game.choiceP2, "mando");
    game.state = "feedback";
    render();
  };
}

function renderFeedback() {
  const last = game.history[game.history.length - 1];
  screen.innerHTML = `
    ${statsBlock()}
    <h2 class="state-title">Consecuencia inmediata</h2>
    <div><strong>Día ${last.day}</strong> · ${last.event} · ${last.choice}</div>
    <p class="event-desc">${last.flavor}</p>
    <div class="actions"><button id="continueBtn" class="primary">Continuar al siguiente día</button></div>
    <div class="log small">Historial reciente: ${game.history.slice(-4).map((h) => `D${h.day}: ${h.choice}`).join(" · ")}</div>
  `;
  document.getElementById("continueBtn").onclick = () => game.continueFromFeedback();
}

function renderEnd() {
  const preview = game.history.slice(-4);
  screen.innerHTML = `
    ${statsBlock()}
    <h2 class="state-title">${game.finalTitle}</h2>
    <p class="event-desc">${game.finalText}</p>
    <div class="log">
      <div><strong>Resumen:</strong></div>
      <div>Días sobrevividos: ${Math.min(game.day - 1, game.maxDay)}</div>
      <div>Dobles agentes detectados: ${game.discovered.size}/2</div>
      <div class="small">Decisiones clave: ${preview.map((i) => `D${i.day}: ${i.choice}`).join(" · ") || "N/A"}</div>
    </div>
    <div class="actions"><button id="restartBtn" class="primary">Nueva partida</button></div>
  `;
  document.getElementById("restartBtn").onclick = () => {
    game.reset();
    render();
  };
}

function render() {
  if (game.state === "start") renderStart();
  else if (game.state === "event") renderEvent();
  else if (game.state === "resolve") renderResolve();
  else if (game.state === "feedback") renderFeedback();
  else renderEnd();
}

window.addEventListener("keydown", (e) => {
  if (game.state === "event") {
    if (e.key === "1") game.choiceP1 = 0;
    if (e.key === "2") game.choiceP1 = 1;
    if (e.key === "3") game.choiceP1 = 2;
    if (e.key.toLowerCase() === "j") game.choiceP2 = 0;
    if (e.key.toLowerCase() === "k") game.choiceP2 = 1;
    if (e.key.toLowerCase() === "l") game.choiceP2 = 2;
    if (e.key === "Enter" && game.choiceP1 !== null && game.choiceP2 !== null) game.resolveChoices();
    render();
  } else if (game.state === "resolve") {
    if (e.key === "ArrowLeft") game.resolveCursor = 0;
    if (e.key === "ArrowRight") game.resolveCursor = 1;
    if (e.key === "Enter") {
      const chosen = game.resolveCursor === 0 ? game.choiceP1 : game.choiceP2;
      game.applyEffect(chosen, "mando");
      game.state = "feedback";
    }
    render();
  } else if (game.state === "feedback" && e.key === "Enter") {
    game.continueFromFeedback();
  } else if (game.state === "start" && e.key === "Enter") {
    game.startEvent();
  }
});

game.reset();
render();
