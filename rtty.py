# rtty.py
import numpy as np
import sounddevice as sd
import threading

# === ПАРАМЕТРЫ RTTY ===
BAUD_RATE = 45.45
BIT_TIME = 1.0 / BAUD_RATE  # ~22 мс на бит
SAMPLE_RATE = 44100
MARK_FREQ  = 1170  # Гц (символ "1")
SPACE_FREQ = 1000  # Гц (символ "0")

baud = BAUD_RATE                                # скорость передачи (по умолчанию 45.45 бод).
mark_freq = MARK_FREQ                      # частота марк  (обычно выше, чем спейс)
space_freq = SPACE_FREQ                    # частота спейс (обычно ниже, чем марк)
amplitude = 0.8                            # амплитуда сигнала (по умолчанию 10 000)
isModulated = False                        # флаг: сигнал сгенерирован (True) или нет.
sample_rate = SAMPLE_RATE                  # частота дискретизации (44 100 Гц).
mark_tone_duration = 0.2                   # 200 мс (длительность маркерного тона в начале и конце передачи)
end_pause_duration = 0.2                   # 200 мс (длительность паузы в конце передачи)

ITA2 = {
    # латинские буквы в стандартном коде ITA2
    'A': [1, 1, 0, 0, 0], 'B': [1, 0, 0, 1, 1], 'C': [0, 1, 1, 1, 0],
    'D': [1, 0, 0, 1, 0], 'E': [1, 0, 0, 0, 0], 'F': [1, 0, 1, 1, 0],
    'G': [0, 1, 0, 1, 1], 'H': [0, 0, 1, 0, 1], 'I': [0, 1, 1, 0, 0],
    'J': [1, 1, 0, 1, 0], 'K': [1, 1, 1, 1, 0], 'L': [0, 1, 0, 0, 1],
    'M': [0, 0, 1, 1, 1], 'N': [0, 0, 1, 1, 0], 'O': [0, 0, 0, 1, 1],
    'P': [0, 1, 1, 0, 1], 'Q': [1, 1, 1, 0, 1], 'R': [0, 1, 0, 1, 0],
    'S': [1, 0, 1, 0, 0], 'T': [0, 0, 0, 0, 1], 'U': [1, 1, 1, 0, 0],
    'V': [0, 1, 1, 1, 1], 'W': [1, 1, 0, 0, 1], 'X': [1, 0, 1, 1, 1],
    'Y': [1, 0, 1, 0, 1], 'Z': [1, 0, 0, 0, 1],
    # цифры/знаки в стандартном коде МТК-2
    '0': [0, 1, 1, 0, 1], '1': [1, 1, 1, 0, 1], '2': [1, 1, 0, 0, 1],
    '3': [1, 0, 0, 0, 0], '4': [0, 1, 0, 1, 0], '5': [0, 0, 0, 0, 1],
    '6': [1, 0, 1, 0, 1], '7': [1, 1, 1, 0, 0], '8': [0, 1, 1, 0, 0],
    '9': [0, 0, 0, 1, 1], '-': [1, 1, 0, 0, 0], '+': [1, 0, 0, 0, 1],
    '?': [1, 0, 0, 1, 1], ':': [0, 1, 1, 1, 0], '(': [1, 1, 1, 1, 0],
    ')': [0, 1, 0, 0, 1], '.': [0, 0, 1, 1, 1], ',': [0, 0, 1, 1, 0],
    '/': [0, 1, 1, 1, 1], ' ': [0, 0, 1, 0, 0],
    'Ш': [0, 1, 0, 1, 1], 'Щ': [0, 0, 1, 0, 1], 'Э': [1, 0, 1, 1, 0],
    'Ю': [1, 1, 0, 1, 0], 'Ч': [0, 1, 0, 1, 0],
    # Русские буквы в стандартном коде МТК-2
    'А': [1, 1, 0, 0, 0], 'Б': [1, 0, 0, 1, 1], 'В': [1, 1, 0, 0, 1],
    'Г': [0, 1, 0, 1, 1], 'Д': [1, 0, 0, 1, 0], 'Е': [1, 0, 0, 0, 0],
    'Ж': [0, 1, 1, 1, 1], 'З': [1, 0, 0, 0, 1], 'И': [0, 1, 1, 0, 0],
    'Й': [1, 1, 0, 1, 0], 'К': [1, 1, 1, 1, 0], 'Л': [0, 1, 0, 0, 1],
    'М': [0, 0, 1, 1, 1], 'Н': [0, 0, 1, 1, 0], 'О': [0, 0, 0, 1, 1],
    'П': [0, 1, 1, 0, 1], 'Р': [0, 1, 0, 1, 0], 'С': [1, 0, 1, 0, 0],
    'Т': [0, 0, 0, 0, 1], 'У': [1, 1, 1, 0, 0], 'Ф': [1, 0, 1, 1, 0],
    'Х': [0, 0, 1, 0, 1], 'Ц': [0, 1, 1, 1, 0], 'Ъ': [1, 0, 1, 1, 1],
    'Ы': [1, 0, 1, 0, 1], 'Ь': [1, 0, 1, 1, 1], 
    'Я': [1, 1, 1, 0, 1], 'Ё': [1, 0, 0, 0, 0],
    'RUS' : [0, 0, 0, 0, 0],  # переключение на русские буквы
    'FIGS': [1, 1, 0, 1, 1],  # переключение на цифры/спецсимволы
    'LAT':  [1, 1, 1, 1, 1],  # переключение на латинские буквы
    '\r':   [0, 0, 0, 1, 0],  # CR (возврат каретки)
    '\n':   [0, 1, 0, 0, 0]   # LF (перевод строки)
}

def _add_bit_sequence(char, bit_array):
    """Добавляет биты символа с старт/стоп-битами в указанный массив."""
    code = ITA2[char]
    sequence = [0] + code + [1, 0.5]
    bit_array.extend(sequence)
    print(f"  Символ: '{char}'")
    print(f"   Биты: {sequence}")

def text_to_baudot(text):
    """Преобразует текст в последовательность битов Baudot (ITA2) с отладочным выводом"""
    #bitArray.clear()
    text = text.upper()
    if not text.strip():
        return []

    bit_array = []
    current_mode = 'LAT'
    bits_length = 0 
    
    print("  Начинаем кодирование Baudot:")
    print("-" * 40)

    # 1. Добавление служебных символов CR + LF в начало передачи
    _add_bit_sequence('LAT', bit_array)               # добавляем в битовый массив (bitArray) код режима LAT
    current_mode = 'LAT'                      # устанавливаем текущий режим LAT
    _add_bit_sequence('\r', bit_array)                # добавляем в битовый массив (bitArray) код символа CR
    _add_bit_sequence('\n', bit_array)                # добавляем в битовый массив (bitArray) код символа LF

    # 2. Кодируем основной текст
    for char in text:                         # Цикл по символам текста: для каждого символа
        if char not in ITA2:                  #   Проверка поддержки: если символ отсутствует в таблице ITA2,
            continue                          #                       пропускаем неподдерживаемые символы

        target_mode = get_char_mode(char)     # Вызываем метод _get_char_mode(char), который по символу char определяет, в каком режиме он должен кодироваться
                                                    # Например, если символ в маасиве 'ABC...XYZ' → возвращает 'LAT'.
        if target_mode != current_mode:        # Проверяет, совпадает ли требуемый режим (target_mode) с текущим режимом объекта (self.current_mode).
                                                    # Если режимы различаются, то
            _add_bit_sequence(target_mode, bit_array) # Вызываем метод _add_char_to_bitarray с аргументом target_mode, который
                                                    # добавляет в битовый массив (bitArray) код переключения режима
                                                    # Например, при переключении на 'RUS' в bitArray добавится:
                                                    # [0, 0, 0, 0, 0, 0, 1, 0.5] (старт + код RUS + стоп + полустоп).
            current_mode = target_mode         # Обновляем текущий режим объекта на новый (target_mode)
                                                    # чтобы не отправлять коды режима до следующего переключения.
        _add_bit_sequence(char, bit_array)            # Вызываем метод _add_char_to_bitarray с аргументом char, который
                                                    # добавляет в битовый массив (bitArray) код символа
                                                    # Например, для символа 'А' в режиме 'RUS' добавится:
                                                    # [0, 1, 1, 0, 0, 0, 1, 0.5] (старт + код RUS + стоп + полустоп).
    # 3. Добавление служебных символов CR + LF в конец
    _add_bit_sequence('\r', bit_array)                # добавляем в битовый массив (bitArray) код символа CR
    _add_bit_sequence('\n', bit_array)                # добавляем в битовый массив (bitArray) код символа LF


    result = bit_array

    print("-" * 40)
    print("  Кодирование завершено\n")
    return bit_array


def get_char_mode(char):
    """
    Определяет режим, к которому относится символ (LAT, FIGS или RUS).
    self — ссылка на создаваемый экземпляр класса,
    char - символ, по которому будет определён режим.
    Метод ожидает заглавные буквы.
    """
    if char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':        # если символ относится к латинским буквам
        return 'LAT'                                # вернуть значение 'LAT'
    elif char in 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЪЫЬЯ':    # если символ относится к русским буквам (за исключением Ч,Ш,Щ,Э,Ю)
        return 'RUS'                                # вернуть значение 'RUS'
    else:                                           # во всех остальных случаях (цифры, знаки препинания, пробел, буквы Ч,Ш,Щ,Э,Ю и др.)
        return 'FIGS'                               # вернуть значение 'FIGS'



def generate_tone(freq, duration, start_phase):
    """Генерирует тон заданной частоты и длительности (на основе синуса)."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False) # t - массив временных отсчётов (через np.linspace)
    # Учитываем начальную фазу
    phase = 2 * np.pi * freq * t + start_phase      # phase — фазовая функция: 2π*freq*t+start_phase
    return (amplitude * np.sin(phase)).astype(np.float32)           # Возвращает: amplitude*sin(phase)

   




def generate_silence(duration):
    """Генерирует тишину (нулевой сигнал) заданной длительности."""
    n_samples = int(sample_rate * duration)    # Вычисляет число отсчётов: int(sample_rate * duration)
    return np.zeros(n_samples)                      # Возвращает np.zeros(n_samples)

def generate_rtty_signal(bitArray):
    """Генерирует FSK‑сигнал без пауз между битами, с 1‑сек паузой в конце."""
    global isModulated
    bit_duration = 1.0 / baud                  # длительность одного бита в секундах
    total_phase = 0.0                               # Текущая фаза сигнала

    # 1. Маркерный тон ПЕРЕД передачей (начинаем с фазы 0)
    pre_mark = generate_tone(mark_freq, mark_tone_duration, 0.0)

    # 2. Сигнал данных (без пауз между битами)
    data_segments = []                              # список сегментов (только биты)
    for bit in bitArray:               # цикл по битам из bitArray
        # Определяем частоту для бита
        if bit == 1 or bit == 0.5:                  # если mark (включая полустоп 1 или 0.5)
            freq = mark_freq                   # частота freq = марк
        else:                                       # иначе - space (0)
            freq = space_freq                  # частота freq = спейс

        # Определяем длительность бита (учитываем полустоп 0.5)
        if bit == 0.5:                              # если полустоп (0.5)
            bit_dur = 0.5 * bit_duration            # длительность bit_dur = 0.5*bit_duration
        else:                                       # иначе (0 или 1)
            bit_dur = bit_duration                  # длительность bit_dur = bit_duration

        # Генерируем сигнал бита в сегмент
        bit_signal = generate_tone(freq, bit_dur, total_phase)  # генерируем сигнал с частотой freq, длительностью bit_dur, фазой total_phase
        data_segments.append(bit_signal)                              # Добавляет сгенерированный звуковой фрагмент (из одного бита/полубита) в список сегментов сигнала
        
        # Обновляем общую фазу для следующего бита
        cycles = freq * bit_dur                     # Количество циклов колебаний за время звучания бита/полубита
        total_phase += 2 * np.pi * cycles           # Переводим количество циклов в фазовый угол (в радианах) 
                                                    # и добавляем этот прирост к текущей фазе total_phase
                                                    # чтобы следующий бит начался с той фазы, на которой закончился предыдущий (плавный переход)
        total_phase %= 2 * np.pi                    # Нормализуем фазу [0, 2π)
                                                    # Операция %= (остаток от деления) «обрубает» лишние полные обороты, оставляя только дробную часть.
    
    # Объединяем все сегменты данных
    data_signal = np.concatenate(data_segments)

    # 3. Маркерный тон ПОСЛЕ передачи
    post_mark = generate_tone(mark_freq, mark_tone_duration, total_phase)

    # 4. Пауза в конце
    end_pause = generate_silence(end_pause_duration)

    # 5. Итоговый сигнал: pre_mark + data_signal + post_mark + end_pause
    signal = np.concatenate([pre_mark, data_signal, post_mark, end_pause]).astype(np.float32)

    
    isModulated = True                         # Устанавливает флаг, что сигнал успешно сгенерирован.
    return signal



def play_rtty(text, on_complete=None):
    """Запускает передачу RTTY в отдельном потоке"""
    if not text.strip():
        print("  Нечего передавать")
        return

    bits = text_to_baudot(text)
    audio_data = generate_rtty_signal(bits)

    # Исправляем тип данных: float32 для sounddevice
    audio_data = np.ascontiguousarray(audio_data, dtype=np.float32)

    def play():
        nonlocal on_complete  # ✅ Сначала объявляем nonlocal
        try:
            print("  ▶️ Начало воспроизведения RTTY...")
            sd.play(audio_data, samplerate=SAMPLE_RATE)
            sd.wait()  # ждём завершения
        finally:
            if on_complete is not None:
                on_complete()
                on_complete = None  # теперь можно обнулить

    threading.Thread(target=play, daemon=True).start()

