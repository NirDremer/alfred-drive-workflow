from workflow import Workflow, PasswordNotFound, ICON_TRASH, ICON_WARNING, ICON_USER
wf = Workflow()
from drive_api import Drive
import httplib2
import json
max_age = 86400 # cache set to one day

class Search:
  def __init__(self,user_input):
    self.user_input = user_input
    self.url = 'https://www.googleapis.com/drive/v2/files?orderBy=lastViewedByMeDate+desc&q=title+contains+\'%s\'&fields=items' % user_input

  def show_items(self):
    wf.logger.error('showing items')
    # links = self.get_links()
    # add max age later
    links = wf.cached_data(self.user_input,self.get_links)
    self.add_items(links)

  #TODO: use wf.stored_data
  def get_links(self):
    user_input = escape_term(self.user_input)
    user_credentials = Drive.get_credentials()
    http = httplib2.Http()
    http = user_credentials.authorize(http)
    (resp_headers, content) = http.request(self.url,'GET')
    unfiltered_list = json.loads(content)['items']
    return filter_by_file_type(unfiltered_list,['spreadsheet','document'])

  def add_items(self, links):
    if len(links):
      wf.logger.error('there are links')
      # sorted(links, key=lambda link : link['lastViewedByMeDate'])
      count = 0
      for index, link in enumerate(links):
        count += 1
        title = link['title']
        alternateLink = link['alternateLink']
        icon = link['icon']
        wf.add_item(
          title=title,
          arg=alternateLink,
          icon=icon,
          valid=True
        )
      if count == 0:
        wf.add_item(
          title='No files found',
          icon=ICON_WARNING,
        )
    else:
      wf.add_item(
        title='No files found',
        icon=ICON_WARNING,
      )
    wf.send_feedback()

def filter_by_file_type(list, file_types):
  filter_list = []
  for index, link in enumerate(list):
    type = ''
    try:
      type = link['mimeType'].split('.')[2]
    except:
      wf.logger.error('title' + link['mimeType'])
    if type in file_types:
      # refactor
      icon = './assets/sheets.png' if type == 'spreadsheet' else './assets/docs.png'
      link['icon'] = icon
      link['type'] = type
      filter_list.append(link)

  return filter_list

def escape_term(term):
  return term.replace(' ', '+')

