# SlideShare & Adobe Indesign Presentation Scraper

This project consists of two Python scripts designed to scrape and process presentations embedded on specific platforms (SlideShare.net and Adobe Indesign) from various websites. The scripts automatically capture screenshots of each slide from the presentations and compile them into a PDF document.

## Features

- **Supports scraping from two platforms**: 
  - `v1.py` scrapes presentations from SlideShare links (2017-2022).
  - `v2.py` scrapes presentations from Adobe Indesign links (2023 onwards).
  
- **Automated screenshot capture**: Both scripts capture individual slides from the presentations as screenshots using Selenium WebDriver.

- **PDF generation**: The screenshots are compiled into a PDF file for easy viewing and sharing.

- **Cookie handling**: The scripts include mechanisms to accept cookie consent dialogs automatically.

## Requirements

To run the scripts, ensure you have the following installed:

- Python 3.x
- [Selenium](https://selenium-python.readthedocs.io/) for browser automation
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [FPDF](http://www.fpdf.org/) for PDF creation
- [Pillow](https://pillow.readthedocs.io/) for image processing
- [WebDriver Manager](https://pypi.org/project/webdriver-manager/) to manage WebDriver binaries for Selenium

You can install the dependencies via `pip`:

```bash
pip install selenium beautifulsoup4 fpdf pillow webdriver-manager
```

### v1.py: SlideShare Scraper

This script is designed to scrape presentations from SlideShare embedded in various reports published between 2017 and 2022.

1. **Link Collection**: It parses each provided page URL to extract iframe `src` links pointing to SlideShare presentations.
2. **Screenshot Capture**: It automates the navigation through the presentation slides using Selenium.
3. **PDF Generation**: After capturing all slides, it compiles them into a single PDF file.

### v2.py: Adobe Indesign Scraper

This script is designed to scrape presentations from Adobe Indesign embedded in reports from 2023 onwards.

1. **Iframe Scraping**: It collects iframe `src` links containing `indd.adobe.com`.
2. **Screenshot Capture**: Like `v1.py`, this script navigates through each slide and captures screenshots.
3. **PDF Generation**: The captured screenshots are compiled into a PDF file.

## Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/presentation-scraper.git
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the desired script:

   - For SlideShare (2017-2022):
     ```bash
     python v1.py
     ```

   - For Adobe Indesign (2023 onwards):
     ```bash
     python v2.py
     ```

Both scripts will process the provided URLs, capture the slides, and save them as a PDF in the corresponding presentation folder.

## Customization

You can modify the list of URLs to target different reports. Simply edit the `page_urls` array in either script to include the desired links.

## Known Issues

- Ensure that the browser driver (Chrome) is compatible with the installed browser version.
- The scripts rely on page structure; if the website structure changes, adjustments to the scraping logic may be required.
- Some presentations might have security or content restrictions that prevent scraping.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

---

Let me know if you need any additional adjustments or have other requests!
