import re

drum_channel = "9"
name_pattern = re.compile(r'^(.+)\/([^/]+)\.(.*)$')
comment_pattern = re.compile(r'\s*[\#\;]')
tempo_pattern = re.compile(r'(\d+),\s*(\d+),\s*(Tempo),\s*(\d+)')
track_pattern = re.compile(r'\s*(\d+)\s*,\s*\d+\s*,\s*\w+_c\s*,\s*(\d+)')
channel_pattern = re.compile(r'\s*\d+\s*,\s*\d+\s*,\s*\w+_c\s*,\s*(\d+)')
lyric_pattern = re.compile(r'\s*\d+\s*,\s*\d+\s*,\s*(\w+_t)\s*,\s*"(.*)"')
note_pattern = re.compile(r'(\d+),\s*(\d+),\s*(Note_\w+),\s*(\d+),\s*(\d+),\s*(\d+)')
key_signature_pattern = re.compile(r'(\d+),\s*(\d+),\s*(Key_signature),\s*(\d+),\s*"(\w+)"')
time_signature_pattern = re.compile(r'(\d+),\s*(\d+),\s*(Time_signature),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)')
unknown_event_pattern = re.compile(r'(\d+),\s*(\d+),\s*(Unknown_meta_event),.*')
sequencer_specific_pattern = re.compile(r'(\d+),\s*(\d+),\s*(Sequencer_specific),.*')
system_exclusive_pattern = re.compile(r'(\d+),\s*(\d+),\s*(System_exclusive\w*),.*')
program_change_pattern = re.compile(r'(\d+),\s*(\d+),\s*(Program_c),\s*(\d+),\s*(\d+)')
