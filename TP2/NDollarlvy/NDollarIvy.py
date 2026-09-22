import pygame
import pickle
import os
from ndollar import Point, NDollarRecognizer
from ivy.ivy import IvyServer

class NDollarApp(IvyServer):
    def __init__(self, dict_file="gestures.pickle"):
        IvyServer.__init__(self, 'NDollarIvy')
        self.start('127.255.255.255:2010')
        self.recognizer = NDollarRecognizer()
        
        self.candidate_strokes = []
        self.current_stroke = []
        self.dict_file = dict_file
        
        self.last_name = "Aucun"
        self.last_score = 0.0
        self.mouse_down = False
        
        self.load_templates()

    def process_recognition(self):
        if len(self.candidate_strokes) > 0:
            name, score = self.recognizer.recognize(self.candidate_strokes)
            self.last_name = name
            self.last_score = score
            if score > 0.60:
                self.send_msg(f'NDollarIvy Recognized={name} Confidence={score:.2f}')
            self.candidate_strokes = []

    def load_templates(self):
        if os.path.exists(self.dict_file):
            with open(self.dict_file, 'rb') as f:
                data = pickle.load(f)
                for name, strokes in data:
                    self.recognizer.add_template(name, strokes)
            print(f"{len(self.recognizer.templates)} modèles chargés.")

    def add_new_gesture(self):
        if len(self.candidate_strokes) > 0:
            # Demande le nom dans le terminal
            name = input("Entrez le nom du nouveau geste : ")
            
            data = []
            if os.path.exists(self.dict_file):
                with open(self.dict_file, 'rb') as f:
                    data = pickle.load(f)
            
            data.append((name, self.candidate_strokes))
            with open(self.dict_file, 'wb') as f:
                pickle.dump(data, f)
                
            self.recognizer.add_template(name, self.candidate_strokes)
            self.candidate_strokes = []
            self.last_name = f"Appris: {name}"
            print(f"Geste '{name}' sauvegardé dans {self.dict_file}.")

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((640, 640))
    pygame.display.set_caption('$N Multistroke Recognizer')
    font = pygame.font.SysFont('hack', 20)
    clock = pygame.time.Clock()
    
    app = NDollarApp()
    done = False
    
    while not done:
        screen.fill((200, 200, 200))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    app.process_recognition()
                elif event.key == pygame.K_a:
                    app.add_new_gesture()
                elif event.key == pygame.K_ESCAPE:
                    done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                app.mouse_down = True
                x, y = pygame.mouse.get_pos()
                app.current_stroke = [Point(x, y)]
            elif event.type == pygame.MOUSEMOTION:
                if app.mouse_down:
                    x, y = pygame.mouse.get_pos()
                    app.current_stroke.append(Point(x, y))
            elif event.type == pygame.MOUSEBUTTONUP:
                app.mouse_down = False
                if len(app.current_stroke) > 5:
                    app.candidate_strokes.append(app.current_stroke)
                app.current_stroke = []

        # Dessin des traits
        for stroke in app.candidate_strokes:
            if len(stroke) > 1:
                pygame.draw.lines(screen, (0, 0, 0), False, [(p.x, p.y) for p in stroke], 3)
                
        if len(app.current_stroke) > 1:
            pygame.draw.lines(screen, (255, 0, 0), False, [(p.x, p.y) for p in app.current_stroke], 3)

        # UI
        screen.blit(font.render(f"Reconnu: {app.last_name} (Score: {app.last_score:.2f})", True, (0, 0, 0)), (20, 20))
        screen.blit(font.render("Espace = Reconnaître | A = Apprendre | Echapp = Quitter", True, (100, 100, 100)), (20, 50))
        
        pygame.display.flip()
        clock.tick(60)

    app.stop()
    pygame.quit()