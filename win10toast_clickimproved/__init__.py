# === context ===

# 1: Original module: https://github.com/jithurjacob/Windows-10-Toast-Notifications 

# 2: Tweaked version (support for notifications that persist in the notification center):
# https://github.com/tnthieding/Windows-10-Toast-Notifications

# **This fork** is an improved version of 2 ^ with `callback_on_click` that allows to run a function on notification
# click, for example to open a URL.

# === installation of the module === 

# pip install win10toast-click

# === let's go === 

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__all__ = ['ToastNotifier']

# #############################################################################
# ########## Libraries #############
# ##################################
# standard library
import logging
import threading
import time
from os import path
from time import sleep
from pkg_resources import Requirement
from pkg_resources import resource_filename

# 3rd party modules
from win32api import GetModuleHandle
from win32api import PostQuitMessage
from win32con import CW_USEDEFAULT
from win32con import IDI_APPLICATION
from win32con import IMAGE_ICON
from win32con import LR_DEFAULTSIZE
from win32con import LR_LOADFROMFILE
from win32con import WM_DESTROY
from win32con import WM_USER
from win32con import WS_OVERLAPPED
from win32con import WS_SYSMENU
from win32gui import CreateWindow
from win32gui import DestroyWindow
from win32gui import LoadIcon
from win32gui import LoadImage
from win32gui import NIF_ICON
from win32gui import NIF_INFO
from win32gui import NIF_MESSAGE
from win32gui import NIF_TIP
from win32gui import NIM_ADD
from win32gui import NIM_DELETE
from win32gui import NIM_MODIFY
from win32gui import RegisterClass
from win32gui import UnregisterClass
from win32gui import Shell_NotifyIcon
from win32gui import UpdateWindow
from win32gui import WNDCLASS

# === click handler piece ===
from win32gui import PumpMessages
# Magic constants
PARAM_DESTROY = 1028
PARAM_CLICKED = 1029

# ############################################################################
# ########### Classes ##############
# ##################################


class ToastNotifier(object):
    """Create a Windows 10  toast notification.
    from: https://github.com/jithurjacob/Windows-10-Toast-Notifications
    """

    def __init__(self):
        """Initialize."""
        self._thread = None

    @staticmethod
    def _decorator(func, callback=None, cb_args=None):
        """
        :param func: callable to decorate
        :param callback: callable to run on mouse click within notification window
        :param cb_args: list of arguments to pass to the callable
        :type cb_args: list
        :return: callable
        """
        def inner(*args, **kwargs):
            kwargs.update({'callback': callback, 'cb_args': cb_args})
            func(*args, **kwargs)
        return inner

    def _show_toast(self, title, msg,
                    icon_path, duration, callback_on_click, cb_args):
        """

        :param title: The title of the notification
        :param msg: The body of the notification
        :param icon_path: The icon to display
        :param duration: How long to display the notification
        :type duration: int
        :param callback_on_click: The method to call when the notification is clicked
        :param cb_args: A list of arguments to pass to the method when clicked
        :type cb_args: list
        :return:
        """
        """Notification settings.
        :title: notification title
        :msg: notification message
        :icon_path: path to the .ico file to custom notification
        :duration: delay in seconds before notification self-destruction, None for no-self-destruction
        """
        message_map = {WM_DESTROY: self.on_destroy, }

        # Register the window class.
        self.wc = WNDCLASS()
        self.hinst = self.wc.hInstance = GetModuleHandle(None)
        self.wc.lpszClassName = str("PythonTaskbar" + str(time.time()).replace('.', ''))  # must be a string
        # self.wc.lpfnWndProc = message_map  # could also specify a wndproc.
        self.wc.lpfnWndProc = self._decorator(self.wnd_proc, callback_on_click, cb_args)  # could instead specify simple mapping
        try:
            self.classAtom = RegisterClass(self.wc)
        except Exception as e:
            # pass # not sure of this
            logging.error("Some trouble with classAtom ({})".format(e))
        style = WS_OVERLAPPED | WS_SYSMENU
        self.hwnd = CreateWindow(self.classAtom, "Taskbar", style,
                                 0, 0, CW_USEDEFAULT,
                                 CW_USEDEFAULT,
                                 0, 0, self.hinst, None)
        UpdateWindow(self.hwnd)

        # icon
        if icon_path is not None:
            icon_path = path.realpath(icon_path)
        else:
            icon_path = resource_filename(Requirement.parse("win10toast_clickimproved"),
                                          "win10toast_clickimproved/icon/notification.ico")
        icon_flags = LR_LOADFROMFILE | LR_DEFAULTSIZE
        try:
            hicon = LoadImage(self.hinst, icon_path,
                              IMAGE_ICON, 0, 0, icon_flags)
        except Exception as e:
            logging.error("Some trouble with the icon ({}): {}"
                          .format(icon_path, e))
            hicon = LoadIcon(0, IDI_APPLICATION)

        # Taskbar icon
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, WM_USER + 20, hicon, "Tooltip")
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY, (self.hwnd, 0, NIF_INFO,
                                      WM_USER + 20,
                                      hicon, "Balloon Tooltip", msg, 200,
                                      title))
        PumpMessages()
        # take a rest then destroy
        if duration is not None:
            sleep(duration)
            DestroyWindow(self.hwnd)
            UnregisterClass(self.wc.lpszClassName, None)
        return None

    def show_toast(self, title="Notification", msg="Here comes the message",
                    icon_path=None, duration=5, threaded=False, callback_on_click=None, cb_args=None):
        """

        :param title: The title of the notification
        :type title: str
        :param msg: The body of the notification
        :type msg: str
        :param icon_path: The icon to display
        :param duration: How long the notification will persist
        :type duration: int
        :param threaded: I think this was for sending simultaneous notifications, but it hasn't worked and I don't need it
        :type threaded: bool
        :param callback_on_click: The method name to call when the notification is clicked (do not call it)
        :param cb_args: The arguments to pass to the called method
        :type cb_args: list
        :return:
        """
        """Notification settings.
        :title: notification title
        :msg: notification message
        :icon_path: path to the .ico file to custom notification
        :duration: delay in seconds before notification self-destruction, None for no-self-destruction
        """
        if not threaded:
            self._show_toast(title, msg, icon_path, duration, callback_on_click, cb_args)
        else:
            if self.notification_active():
                # We have an active notification, let is finish so we don't spam them
                return False

            self._thread = threading.Thread(target=self._show_toast, args=(title, msg, icon_path, duration,
                                                                           callback_on_click, cb_args))
            self._thread.start()
        return True

    def notification_active(self):
        """See if we have an active notification showing"""
        if self._thread != None and self._thread.is_alive():
            # We have an active notification, let is finish we don't spam them
            return True
        return False

    def wnd_proc(self, hwnd, msg, wparam, lparam, **kwargs):
        """Messages handler method"""
        if lparam == PARAM_CLICKED:
            # callback goes here
            if kwargs.get('callback'):
                if kwargs.get('cb_args'):
                    kwargs.pop('callback')(*kwargs.pop('cb_args'))
                else:
                    kwargs.pop('callback')()
            self.on_destroy(hwnd, msg, wparam, lparam)
        elif lparam == PARAM_DESTROY:
            self.on_destroy(hwnd, msg, wparam, lparam)

    def on_destroy(self, hwnd, msg, wparam, lparam):
        """Clean after notification ended.
        :hwnd:
        :msg:
        :wparam:
        :lparam:
        """
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0)

        return None

        # !FIX: TypeError: 'tuple' object is not callable
