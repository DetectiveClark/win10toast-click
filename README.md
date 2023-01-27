# win10toast-clickimproved

>An easy-to-use Python library for displaying Windows 10 Toast Notifications. Improved version of [win10toast](https://pypi.org/project/win10toast/) and [win10toast-persist](https://pypi.org/project/win10toast-persist/) to include `callback_on_click` to run a function on notification click, for example to open a URL.

## Example

```python
# modules
import webbrowser
from win10toast_clickimproved import ToastNotifier


# function 


def open_url(page_url):
    try:
        webbrowser.open_new(page_url)
        print('Opening URL...')
    except:
        print('Failed to open URL. Unsupported variable type.')


# initialize 
toaster = ToastNotifier()
# showcase
page_urls = ['http://example1.com/', 'http://example2.com/', 'http://example3.com/', 'http://example4.com/']
for page in page_urls:
    toaster.show_toast(
        "Example two",  # title
        "Click to open URL! >>",  # message 
        icon_path=None,  # 'icon_path' 
        duration=5,  # for how many seconds toast should be visible; None = leave notification in Notification Center
        threaded=True,
        # True = run other code in parallel; False = code execution will wait till notification disappears 
        callback_on_click=open_url,  # click notification to run function 
        cb_args=[page]  # Arguments to pass to the method.  Must be in the same order they appear in the method.
    )
```

## License

![](https://img.shields.io/github/license/vardecab/win10toast-click)
<!-- GNU General Public License v3. -->

## Acknowledgements
### Original modules
- [win10toast](https://pypi.org/project/win10toast/)
- [win10toast-persist](https://pypi.org/project/win10toast-persist/)
### Stack Overflow
- [click Windows 10 notification to open URL](https://stackoverflow.com/questions/63867448/interactive-notification-windows-10-using-python)
### Packaging & distribution 
- [Packaging Python Projects](https://packaging.python.org/tutorials/packaging-projects/)
- [`setuptools` Quickstart](https://setuptools.readthedocs.io/en/latest/userguide/quickstart.html#including-data-files)
- [Data Files Support](https://setuptools.readthedocs.io/en/latest/userguide/datafiles.html)
- [Configuring setup() using setup.cfg files](https://setuptools.readthedocs.io/en/latest/userguide/declarative_config.html)
- [pypa packaging-problems](https://github.com/pypa/packaging-problems/issues)
### Icon
- [Flaticon / Freepik](https://www.flaticon.com/)

## Contributing

![](https://img.shields.io/github/issues/vardecab/win10toast-click)