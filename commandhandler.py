import pyautogui


def handle_command(command):
    lst = command.split(" ")
    if lst[0] == 'move':
        x = int(lst[1])
        y = int(lst[2])
        (mousex, mousey) = pyautogui.position()
        pyautogui.moveTo(mousex + x, mousey + y)
    else:
        if lst[0] == 'click':
            pyautogui.doubleClick()
