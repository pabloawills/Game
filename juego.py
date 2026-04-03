#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agencia Espectral: Doble Fondo
==============================

Instalación:
1) pip install pygame
2) python juego.py

Controles:
- Menús / lectura:
  - ENTER: avanzar / confirmar
  - ESC: salir
- Selección del Jugador 1 (Operaciones): teclas 1, 2, 3
- Selección del Jugador 2 (Contrainteligencia): teclas J, K, L
- Cuando ambos votan distinto, decide la dirección de turno:
  - Jugador con mando (alterna por ronda) usa FLECHA IZQ / FLECHA DER + ENTER

Objetivo:
- Sobrevivir 12 rondas manteniendo la agencia operativa.
- Tomar decisiones de alto riesgo bajo presión de tiempo.
- Descubrir al menos a uno de los dobles agentes antes del cierre.
"""

import json
import random
import sys
import pygame


# --------------------------- Configuración visual ---------------------------
WIDTH, HEIGHT = 1100, 700
FPS = 60
BG = (17, 20, 26)
PANEL = (27, 32, 42)
TEXT = (229, 233, 240)
MUTED = (165, 173, 186)
GOOD = (120, 220, 140)
BAD = (238, 98, 98)
ALERT = (255, 190, 85)
CYAN = (120, 220, 255)
PURPLE = (180, 140, 255)


# ------------------------------ Utilidades ---------------------------------
def clamp(value, low, high):
    return max(low, min(high, value))


def draw_text(surface, text, font, color, rect, line_height=1.25):
    """Renderiza texto multilínea con ajuste simple de ancho."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        test = word if not current else current + " " + word
        if font.size(test)[0] <= rect.width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    y = rect.y
    step = int(font.get_linesize() * line_height)
    for line in lines:
        img = font.render(line, True, color)
        surface.blit(img, (rect.x, y))
        y += step


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Agencia Espectral: Doble Fondo")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont("consolas", 20)
        self.font_mid = pygame.font.SysFont("consolas", 26)
        self.font_big = pygame.font.SysFont("consolas", 44, bold=True)

        self.running = True
        self.state = "start"

        self.seed = random.randint(10000, 99999)
        self.rng = random.Random(self.seed)

        self.players = ["Operaciones (J1)", "Contrainteligencia (J2)"]
        self.control_owner = 0

        self.all_agents = [
            "Irene Quiralte", "Maksim Volkov", "Padma Rao", "Salvador Urrutia",
            "Amina Djebar", "Tomás Bellido", "Luca Ferrer", "Mireya Cifuentes"
        ]
        self.double_agents = set(self.rng.sample(self.all_agents, 2))

        self.special_events = self.build_events()
        self.reset_game_data()

    def reset_game_data(self):
        self.day = 1
        self.max_day = 12

        self.fondos = 70
        self.influencia = 40
        self.seguridad = 65
        self.sospecha = 15

        self.intel = 15
        self.stress = 10
        self.objetivos = 0
        self.discovered = set()

        self.flags = {
            "vendiste_prototipo": False,
            "rescataste_lena": False,
            "guardaste_silencio_sobre_ministro": False,
            "activaste_bloqueo_total": False,
            "pacto_con_mafia": False,
            "quemaste_archivo_ursula": False,
        }

        self.delayed_effects = []
        self.history = []

        self.current_event = None
        self.current_options = []
        self.timer = 40.0
        self.choice_p1 = None
        self.choice_p2 = None
        self.resolve_cursor = 0

        self.final_title = ""
        self.final_text = ""

    def build_events(self):
        # Eventos diseñados para tener pros/contras y consecuencias diferidas.
        return [
            {
                "id": "puerto_fantasma",
                "name": "Operación Puerto Fantasma",
                "desc": "Entras al almacén del muelle 14. El informante Néstor Cline dice que hay un microfilm, pero huele a trampa de la Oficina Gris.",
                "options": [
                    ("Asaltar ya con equipo pesado", {"fondos": -12, "seguridad": +8, "sospecha": +12, "intel": +14}),
                    ("Sobornar al estibador Vela para entrar sin ruido", {"fondos": -18, "sospecha": -5, "intel": +9, "influencia": +4}),
                    ("Dejarlo correr y vigilar 48h", {"seguridad": -6, "intel": +4, "sospecha": -2, "delay": (2, {"intel": +12, "sospecha": +7})}),
                ],
            },
            {
                "id": "cena_diplomatica",
                "name": "Cena en Embajada Nival",
                "desc": "Te sientas junto al ministro Oskar Venn. Sonríe como quien ya vendió tu funeral. Sobre la mesa: acceso a cuentas cifradas.",
                "options": [
                    ("Filtrar un rumor falso para medir fugas", {"intel": +10, "sospecha": +9, "delay": (2, {"seguridad": +6})}),
                    ("Pagar al maître para cambiar su copa", {"fondos": -10, "influencia": +7, "sospecha": +4, "intel": +6}),
                    ("Callarte y observar", {"influencia": -4, "sospecha": -3, "intel": +3, "flag": "guardaste_silencio_sobre_ministro"}),
                ],
            },
            {
                "id": "tren_orfeo",
                "name": "Tren Orfeo a las 03:10",
                "desc": "Subes al vagón comedor. Lena Arce, analista desaparecida, te mira por el reflejo de una cuchara. No sabes si está asustada o vendida.",
                "options": [
                    ("Extraer a Lena por fuerza", {"seguridad": +5, "fondos": -15, "intel": +7, "flag": "rescataste_lena", "delay": (3, {"intel": +14})}),
                    ("Seguirla sin intervenir", {"intel": +11, "sospecha": +8, "delay": (2, {"seguridad": -8})}),
                    ("Filtrar su ubicación a la prensa", {"influencia": -8, "sospecha": -7, "fondos": +8, "intel": -6}),
                ],
            },
            {
                "id": "subasta_negra",
                "name": "Subasta Negra de Tallin",
                "desc": "Te infiltras en una subasta donde venden el prototipo Asterión. Es ilegal hasta para tus estándares, y eso ya es decir bastante.",
                "options": [
                    ("Comprar el prototipo", {"fondos": -25, "seguridad": +12, "intel": +6}),
                    ("Robarlo durante el apagón", {"seguridad": -10, "sospecha": +14, "intel": +10}),
                    ("Vender tus planos viejos por liquidez", {"fondos": +20, "influencia": -8, "flag": "vendiste_prototipo", "delay": (3, {"seguridad": -10, "sospecha": +10})}),
                ],
            },
            {
                "id": "cloaca_digital",
                "name": "Cloaca Digital",
                "desc": "La hacker Úrsula Brea te ofrece acceso al servidor enemigo. Pide una cosa simple: que quemes su expediente en tus archivos.",
                "options": [
                    ("Aceptar trato con Úrsula", {"intel": +15, "sospecha": +6, "flag": "quemaste_archivo_ursula", "delay": (2, {"influencia": +8})}),
                    ("Detener a Úrsula y copiar su disco", {"seguridad": +8, "intel": +5, "sospecha": +5, "influencia": -4}),
                    ("Ignorarla y reforzar firewall", {"seguridad": +4, "intel": -3, "sospecha": -2}),
                ],
            },
            {
                "id": "frontera_muda",
                "name": "Frontera Muda",
                "desc": "Entras en un puesto fronterizo con papeles falsos. Un capitán te reconoce por una cicatriz que no debería conocer.",
                "options": [
                    ("Activar bloqueo total de comunicaciones", {"seguridad": +14, "influencia": -9, "fondos": -8, "flag": "activaste_bloqueo_total"}),
                    ("Negociar paso con contrabandista Jarek", {"fondos": -6, "intel": +10, "flag": "pacto_con_mafia", "delay": (2, {"sospecha": +10, "fondos": +10})}),
                    ("Retirada táctica con señuelos", {"seguridad": -4, "sospecha": -4, "intel": +6}),
                ],
            },
            {
                "id": "auditoria",
                "name": "Auditoría Interna Fantasma",
                "desc": "Llegan inspectores con sonrisas fotocopiadas. Quieren cuentas, nombres y por qué hay pólvora en la cafetera.",
                "options": [
                    ("Abrir libros reales", {"fondos": -5, "sospecha": -10, "influencia": -5}),
                    ("Fabricar contabilidad creativa", {"fondos": +10, "sospecha": +11, "delay": (2, {"influencia": -9})}),
                    ("Invitar inspectores a una misión de campo", {"seguridad": +6, "influencia": +5, "fondos": -8, "sospecha": +3}),
                ],
            },
            {
                "id": "catedral_humo",
                "name": "La Catedral de Humo",
                "desc": "Bajas a la cripta donde se reúne el Círculo Sal. Hablan en acertijos y te ofrecen un nombre... a cambio de otro.",
                "options": [
                    ("Entregar un agente menor", {"intel": +12, "influencia": -10, "sospecha": +5}),
                    ("Rechazar trato y plantar micro", {"seguridad": +7, "intel": +6, "fondos": -7}),
                    ("Dar nombre falso de alto rango", {"intel": +9, "sospecha": +9, "delay": (3, {"seguridad": -12})}),
                ],
            },
            {
                "id": "hospital_nocturno",
                "name": "Hospital de Noche San Telmo",
                "desc": "Un agente en coma susurra tres letras: 'M.V.'. El doctor Soria pide dinero o silencio. No ofrece descuento por ambos.",
                "options": [
                    ("Pagar tratamiento completo", {"fondos": -16, "intel": +8, "seguridad": +4}),
                    ("Trasladar al agente a base secreta", {"seguridad": +8, "sospecha": +6, "fondos": -6}),
                    ("Cortar soporte y extraer datos", {"intel": +14, "sospecha": +12, "influencia": -7}),
                ],
            },
        ]

    # -------------------------- Generación de eventos --------------------------
    def pick_event(self):
        ev = self.rng.choice(self.special_events)
        self.current_event = ev
        self.current_options = ev["options"]

        self.timer = 40.0
        self.choice_p1 = None
        self.choice_p2 = None
        self.resolve_cursor = 0

    def apply_effect(self, option_index, source="manual"):
        label, effects = self.current_options[option_index]

        self.fondos += effects.get("fondos", 0)
        self.influencia += effects.get("influencia", 0)
        self.seguridad += effects.get("seguridad", 0)
        self.sospecha += effects.get("sospecha", 0)
        self.intel += effects.get("intel", 0)
        self.stress += self.rng.randint(1, 4)

        flag = effects.get("flag")
        if flag:
            self.flags[flag] = True

        if "delay" in effects:
            rounds, delayed = effects["delay"]
            self.delayed_effects.append((self.day + rounds, delayed, label))

        # Consecuencia visible inmediata narrativa.
        flavor = self.build_flavor_text(label, effects)
        self.history.append({
            "day": self.day,
            "event": self.current_event["name"],
            "choice": label,
            "source": source,
            "flavor": flavor,
        })

        # Ajustes y límites.
        self.fondos = clamp(self.fondos, -20, 130)
        self.influencia = clamp(self.influencia, 0, 120)
        self.seguridad = clamp(self.seguridad, 0, 120)
        self.sospecha = clamp(self.sospecha, 0, 140)
        self.intel = clamp(self.intel, 0, 140)
        self.stress = clamp(self.stress, 0, 120)

        # Progresión por umbral de inteligencia.
        if self.intel >= 30 and self.objetivos == 0:
            self.objetivos = 1
        elif self.intel >= 55 and self.objetivos == 1:
            self.objetivos = 2
        elif self.intel >= 85 and self.objetivos == 2:
            self.objetivos = 3

        self.try_discover_double_agent()

    def build_flavor_text(self, label, effects):
        lines = [f"Decides: {label}."]
        if effects.get("sospecha", 0) > 0:
            lines.append("Notas cámaras que antes no estaban. Alguien también te está cazando.")
        if effects.get("seguridad", 0) < 0:
            lines.append("Tu red tiembla. Dos claves maestras dejaron de responder.")
        if effects.get("fondos", 0) < -12:
            lines.append("El tesorero te mira como si acabaras de prender fuego al presupuesto anual.")
        if effects.get("intel", 0) >= 10:
            lines.append("El rompecabezas encaja un poco más... y te gusta menos lo que ves.")
        if not lines:
            return "La noche pasa sin héroes. Solo con consecuencias."
        return " ".join(lines)

    def apply_delayed_effects(self):
        pending = []
        for target_day, delayed, origin in self.delayed_effects:
            if target_day <= self.day:
                self.fondos += delayed.get("fondos", 0)
                self.influencia += delayed.get("influencia", 0)
                self.seguridad += delayed.get("seguridad", 0)
                self.sospecha += delayed.get("sospecha", 0)
                self.intel += delayed.get("intel", 0)
                txt = f"Efecto tardío de '{origin}': "
                txt += ", ".join([f"{k} {v:+d}" for k, v in delayed.items()])
                self.history.append({"day": self.day, "event": "Consecuencia diferida", "choice": origin, "source": "delay", "flavor": txt})
            else:
                pending.append((target_day, delayed, origin))
        self.delayed_effects = pending

    def try_discover_double_agent(self):
        # Información oculta: descubrir traidores depende de intel/sospecha y azar.
        chance = 0.08 + self.intel / 250.0 + self.sospecha / 500.0
        if self.rng.random() < chance:
            unknown = list(self.double_agents - self.discovered)
            if unknown:
                found = self.rng.choice(unknown)
                self.discovered.add(found)
                self.history.append({
                    "day": self.day,
                    "event": "Filtración interceptada",
                    "choice": "Nombre revelado",
                    "source": "intel",
                    "flavor": f"Tu analista cifra una llamada y pronuncia un nombre con la voz rota: {found}."
                })
                self.seguridad += 5
                self.sospecha += 3

    # ----------------------------- Flujo de juego -----------------------------
    def next_day(self):
        self.day += 1
        self.control_owner = 1 - self.control_owner

    def loss_reason(self):
        if self.seguridad <= 0:
            return "Tu red cae en una madrugada. Puertas abiertas, archivos vacíos y sirenas en el pasillo."
        if self.fondos <= 0:
            return "Te quedas sin fondos. Los leales aceptan mejores sueldos en agencias peores."
        if self.sospecha >= 100:
            return "Tu tapadera colapsa. Tu cara aparece en portadas antes del café de la mañana."
        if self.stress >= 100:
            return "El mando se fragmenta. Ninguna orden llega intacta y todo se vuelve ruido."
        return None

    def compute_ending(self):
        traitor_score = len(self.discovered)
        win = self.day > self.max_day and self.objetivos >= 3 and self.seguridad > 10 and self.fondos > 10

        if win and traitor_score >= 2:
            self.final_title = "FINAL: Monarca de Sombras"
            self.final_text = "Sobrevives 12 rondas, expones a ambos dobles agentes y negocias desde fuerza. Nadie te aplaude, pero todos te temen."
        elif win:
            self.final_title = "FINAL: Victoria Hueca"
            self.final_text = "Sostienes la agencia a duras penas. Ganas la guerra pública, pero alguien sigue filtrando desde dentro."
        elif self.sospecha >= 100:
            self.final_title = "FINAL: Portada Roja"
            self.final_text = "Te conviertes en noticia. El enemigo ni siquiera necesita balas cuando tiene tus errores en horario prime time."
        elif self.fondos <= 0:
            self.final_title = "FINAL: Quiebra Patriótica"
            self.final_text = "Defiendes al país, sí. Con pagarés y una máquina de café empeñada."
        elif self.seguridad <= 0:
            self.final_title = "FINAL: Casa Abierta"
            self.final_text = "Tu edificio sigue en pie, pero ya no es tuyo. Cada cámara mira para otro lado."
        else:
            self.final_title = "FINAL: Cenizas Operativas"
            self.final_text = "No logras cerrar la operación. Quedan cabos sueltos, nombres tachados y una silla vacía en tu despacho."

    def export_summary(self):
        # json de resumen para rejugabilidad y revisión post-partida.
        out = {
            "seed": self.seed,
            "dias": self.day,
            "fondos": self.fondos,
            "influencia": self.influencia,
            "seguridad": self.seguridad,
            "sospecha": self.sospecha,
            "intel": self.intel,
            "objetivos": self.objetivos,
            "dobles_descubiertos": sorted(self.discovered),
            "historial": self.history[-20:],
            "final": self.final_title,
        }
        try:
            with open("resumen_partida.json", "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    # ------------------------------ Render UI --------------------------------
    def draw_panel(self):
        pygame.draw.rect(self.screen, PANEL, (20, 20, WIDTH - 40, HEIGHT - 40), border_radius=12)

        title = self.font_mid.render(f"Día {self.day}/{self.max_day}  |  Semilla {self.seed}", True, CYAN)
        self.screen.blit(title, (40, 36))

        stats = [
            ("Fondos", self.fondos, ALERT),
            ("Influencia", self.influencia, PURPLE),
            ("Seguridad", self.seguridad, GOOD),
            ("Sospecha", self.sospecha, BAD),
            ("Intel", self.intel, CYAN),
            ("Estrés", self.stress, ALERT),
            ("Objetivos", self.objetivos, TEXT),
        ]

        x = 40
        y = 80
        for name, val, col in stats:
            img = self.font_small.render(f"{name}: {val}", True, col)
            self.screen.blit(img, (x, y))
            x += 145

        ctrl = self.font_small.render(f"Mando actual: {self.players[self.control_owner]}", True, MUTED)
        self.screen.blit(ctrl, (40, 115))

        found = ", ".join(sorted(self.discovered)) if self.discovered else "Ninguno confirmado"
        fd = self.font_small.render(f"Dobles agentes detectados: {found}", True, TEXT)
        self.screen.blit(fd, (40, 145))

    def draw_start(self):
        self.screen.fill(BG)
        pygame.draw.rect(self.screen, PANEL, (80, 80, WIDTH - 160, HEIGHT - 160), border_radius=16)

        self.screen.blit(self.font_big.render("AGENCIA ESPECTRAL", True, CYAN), (170, 150))
        self.screen.blit(self.font_big.render("DOBLE FONDO", True, PURPLE), (170, 210))

        lore = (
            "Eres parte de una agencia que protege un país que no sabrá tu nombre. "
            "Hoy sospechas que dos de tus mejores agentes trabajan también para el enemigo."
        )
        draw_text(self.screen, lore, self.font_mid, TEXT, pygame.Rect(170, 300, 760, 130))

        rules = (
            "J1 vota con 1/2/3. J2 vota con J/K/L. Tienen segundos, no minutos. "
            "Sobrevive 12 días, consigue intel y acepta que toda decisión te cobrará después."
        )
        draw_text(self.screen, rules, self.font_small, MUTED, pygame.Rect(170, 415, 760, 100))

        tip = self.font_mid.render("ENTER para empezar   |   ESC para salir", True, ALERT)
        self.screen.blit(tip, (230, 560))

    def draw_event(self):
        self.screen.fill(BG)
        self.draw_panel()

        ev = self.current_event
        name_img = self.font_mid.render(ev["name"], True, TEXT)
        self.screen.blit(name_img, (40, 190))

        draw_text(self.screen, ev["desc"], self.font_small, MUTED, pygame.Rect(40, 230, 1020, 100))

        for i, (label, _) in enumerate(self.current_options):
            y = 350 + i * 90
            box = pygame.Rect(45, y, 1010, 72)
            pygame.draw.rect(self.screen, (34, 40, 51), box, border_radius=8)
            n = self.font_mid.render(f"{i+1}", True, CYAN)
            self.screen.blit(n, (58, y + 20))
            draw_text(self.screen, label, self.font_small, TEXT, pygame.Rect(110, y + 17, 930, 40))

        timer_col = BAD if self.timer < 4 else ALERT
        timer_text = self.font_mid.render(f"Tiempo: {self.timer:0.1f}s", True, timer_col)
        self.screen.blit(timer_text, (870, 190))

        pick1 = "-" if self.choice_p1 is None else str(self.choice_p1 + 1)
        pick2 = "-" if self.choice_p2 is None else str(self.choice_p2 + 1)
        self.screen.blit(self.font_small.render(f"J1 vota: {pick1}", True, CYAN), (40, 640))
        self.screen.blit(self.font_small.render(f"J2 vota: {pick2}", True, PURPLE), (220, 640))

    def draw_resolve(self):
        self.screen.fill(BG)
        self.draw_panel()

        p1 = self.current_options[self.choice_p1][0]
        p2 = self.current_options[self.choice_p2][0]
        owner_name = self.players[self.control_owner]

        title = self.font_mid.render("Votos en conflicto", True, ALERT)
        self.screen.blit(title, (40, 220))
        draw_text(
            self.screen,
            f"Ambos discrepan. {owner_name} decide cuál plan ejecutar. "
            "IZQ elige voto de J1, DER elige voto de J2, ENTER confirma.",
            self.font_small,
            TEXT,
            pygame.Rect(40, 260, 1020, 100),
        )

        for idx, txt in enumerate([p1, p2]):
            x = 80 + idx * 520
            rect = pygame.Rect(x, 390, 440, 170)
            color = CYAN if idx == 0 else PURPLE
            if self.resolve_cursor == idx:
                pygame.draw.rect(self.screen, color, rect, width=4, border_radius=10)
            else:
                pygame.draw.rect(self.screen, (80, 80, 90), rect, width=2, border_radius=10)
            who = "Voto J1" if idx == 0 else "Voto J2"
            self.screen.blit(self.font_small.render(who, True, color), (x + 15, 405))
            draw_text(self.screen, txt, self.font_small, TEXT, pygame.Rect(x + 15, 440, 410, 95))

    def draw_feedback(self):
        self.screen.fill(BG)
        self.draw_panel()

        if not self.history:
            return
        last = self.history[-1]
        self.screen.blit(self.font_mid.render("Consecuencia inmediata", True, ALERT), (40, 220))
        draw_text(
            self.screen,
            f"Día {last['day']} · {last['event']} · {last['choice']}",
            self.font_small,
            CYAN,
            pygame.Rect(40, 260, 1020, 40),
        )
        draw_text(self.screen, last["flavor"], self.font_small, TEXT, pygame.Rect(40, 300, 1020, 160))

        draw_text(
            self.screen,
            "ENTER para continuar al siguiente día.",
            self.font_mid,
            MUTED,
            pygame.Rect(40, 580, 700, 50),
        )

    def draw_end(self):
        self.screen.fill(BG)
        pygame.draw.rect(self.screen, PANEL, (60, 60, WIDTH - 120, HEIGHT - 120), border_radius=16)

        self.screen.blit(self.font_big.render(self.final_title, True, ALERT), (90, 100))
        draw_text(self.screen, self.final_text, self.font_mid, TEXT, pygame.Rect(90, 170, 920, 100))

        facts = [
            f"Días sobrevividos: {min(self.day - 1, self.max_day)}",
            f"Objetivos cumplidos: {self.objetivos}/3",
            f"Fondos finales: {self.fondos}",
            f"Seguridad final: {self.seguridad}",
            f"Sospecha final: {self.sospecha}",
            f"Dobles agentes detectados: {len(self.discovered)}/2",
        ]

        y = 290
        for f in facts:
            self.screen.blit(self.font_small.render(f, True, CYAN), (100, y))
            y += 34

        self.screen.blit(self.font_mid.render("Decisiones clave:", True, PURPLE), (100, 520))
        preview = self.history[-4:]
        py = 560
        for item in preview:
            line = f"D{item['day']} · {item['choice']}"
            self.screen.blit(self.font_small.render(line[:95], True, MUTED), (100, py))
            py += 28

        self.screen.blit(self.font_small.render("ENTER = nueva partida | ESC = salir", True, ALERT), (680, 620))

    # ------------------------------ Input loop -------------------------------
    def handle_event_state_key(self, key):
        if key == pygame.K_1:
            self.choice_p1 = 0
        elif key == pygame.K_2:
            self.choice_p1 = 1
        elif key == pygame.K_3:
            self.choice_p1 = 2

        if key == pygame.K_j:
            self.choice_p2 = 0
        elif key == pygame.K_k:
            self.choice_p2 = 1
        elif key == pygame.K_l:
            self.choice_p2 = 2

    def resolve_choices(self):
        # Si falta voto por tiempo, el sistema completa con elección "segura" aproximada.
        if self.choice_p1 is None:
            self.choice_p1 = self.rng.randint(0, 2)
        if self.choice_p2 is None:
            self.choice_p2 = self.rng.randint(0, 2)

        if self.choice_p1 == self.choice_p2:
            self.apply_effect(self.choice_p1, source="consenso")
            self.state = "feedback"
            return

        # Versus local: el jugador con mando rompe el empate.
        self.resolve_cursor = 0
        self.state = "resolve"

    def update(self, dt):
        if self.state == "event":
            self.timer -= dt
            if self.timer <= 0:
                self.timer = 0
                self.resolve_choices()

    def process_frame(self):
        dt = self.clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if self.state == "start" and event.key == pygame.K_RETURN:
                    self.reset_game_data()
                    self.pick_event()
                    self.state = "event"

                elif self.state == "event":
                    self.handle_event_state_key(event.key)
                    if event.key == pygame.K_RETURN and self.choice_p1 is not None and self.choice_p2 is not None:
                        self.resolve_choices()

                elif self.state == "resolve":
                    if event.key == pygame.K_LEFT:
                        self.resolve_cursor = 0
                    elif event.key == pygame.K_RIGHT:
                        self.resolve_cursor = 1
                    elif event.key == pygame.K_RETURN:
                        chosen = self.choice_p1 if self.resolve_cursor == 0 else self.choice_p2
                        self.apply_effect(chosen, source="mando")
                        self.state = "feedback"

                elif self.state == "feedback" and event.key == pygame.K_RETURN:
                    self.apply_delayed_effects()
                    reason = self.loss_reason()
                    if reason:
                        self.compute_ending()
                        self.final_text = reason + " " + self.final_text
                        self.export_summary()
                        self.state = "end"
                    else:
                        self.next_day()
                        if self.day > self.max_day:
                            self.compute_ending()
                            self.export_summary()
                            self.state = "end"
                        else:
                            self.pick_event()
                            self.state = "event"

                elif self.state == "end" and event.key == pygame.K_RETURN:
                    self.seed = random.randint(10000, 99999)
                    self.rng = random.Random(self.seed)
                    self.double_agents = set(self.rng.sample(self.all_agents, 2))
                    self.state = "start"

        self.update(dt)

        if self.state == "start":
            self.draw_start()
        elif self.state == "event":
            self.draw_event()
        elif self.state == "resolve":
            self.draw_resolve()
        elif self.state == "feedback":
            self.draw_feedback()
        elif self.state == "end":
            self.draw_end()

        pygame.display.flip()

    def run(self):
        while self.running:
            self.process_frame()
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    Game().run()
