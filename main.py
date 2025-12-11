# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.config import Config

from rtty import play_rtty  # импортируем функцию передачи
import sounddevice as sd


Config.set('graphics', 'width', '720')
Config.set('graphics', 'height', '1650')
Config.set('graphics', 'resizable', False)


class RTTYApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=[dp(15), dp(40), dp(15), dp(20)], spacing=dp(16))

        title = Label(text='RTTY Передатчик', font_size=dp(22), size_hint_y=None, height=dp(50), color=(0.3, 0.7, 1, 1), bold=True)
        layout.add_widget(title)

        self.text_input = TextInput(
            hint_text='Введите текст для передачи...',
            multiline=False,
            size_hint_y=None,
            height=dp(70),
            font_size=dp(24),
            halign='center',
            foreground_color=(0.2, 0.6, 1, 1),
            background_color=(0.1, 0.1, 0.15, 1),
            cursor_color=(0.2, 0.6, 1, 1),
            padding=[dp(10), dp(20)]
        )
        layout.add_widget(self.text_input)

        start_btn = Button(text='СТАРТ', size_hint_y=None, height=dp(90), font_size=dp(28), bold=True, background_color=(0.15, 0.65, 0.25, 1), color=(1, 1, 1, 1))
        start_btn.bind(on_press=self.start_rtty)
        layout.add_widget(start_btn)

        stop_btn = Button(text='СТОП', size_hint_y=None, height=dp(90), font_size=dp(28), bold=True, background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        stop_btn.bind(on_press=self.stop_rtty)
        layout.add_widget(stop_btn)

        self.led = Label(text='[]', font_size=dp(40), color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(60))
        layout.add_widget(self.led)

        layout.add_widget(Widget(size_hint_y=0.2))

        self.transmitting = False

        return layout

    def on_start(self):
        self.text_input.focus = True


    def on_pause(self):
        return True

    def start_rtty(self, instance):
        if self.transmitting:
            return
        text = self.text_input.text.strip()
        if not text:
            print("Нечего передавать")
            return
    
        print(f"Передача: '{text}'")
        self.led.color = (0, 1, 0, 1)
        self.transmitting = True
        self.manual_stop = False
    
        play_rtty(text, on_complete=self.on_transmission_complete)


    def on_transmission_complete(self):
        if not self.manual_stop:  # ✅ Только если не было ручной остановки
            print("Передача RTTY завершена")
        else:
            print("Передача была прервана вручную")
        self.led.color = (0.5, 0.5, 0.5, 1)
        self.transmitting = False
        self.manual_stop = False  # Сбросим флаг


    
    def stop_rtty(self, instance):
        if not self.transmitting:
            return  # ✅ Не останавливаем, если не передаём
        self.manual_stop = True
        sd.stop()
        print("Передача остановлена")
        self.led.color = (0.5, 0.5, 0.5, 1)
        self.transmitting = False





if __name__ == '__main__':
    try:
        RTTYApp().run()
    except Exception as e:
        print("Ошибка при запуске приложения:")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter, чтобы выйти...")
