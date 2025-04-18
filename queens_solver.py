from src.board_scrapper.QueensScrapper import QueensScrapper
from src.solver.QueensSolver import QueensSolver
from src.visualizer.QueensPrinter import BoardPrinter
import time
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

SOLVED_BOARDS = 'resources/solved_boards/Queens'
BOARD_INSTANCES = 'resources/instances/Queens'
STYLES = 'resources/variables/styles.json'
WEB_LITERALS = 'resources/variables/html_literals.json'

GAME = 'queens'


def load_json_files():
    with open('resources/variables/html_literals.json') as f:
        web_literals = json.load(f)
    with open('resources/variables/styles.json') as f:
        color_palette = json.load(f)

    return web_literals, color_palette


def load_json(path):
    with open(path) as f:
        json_content = json.load(f)
    return json_content


def fetch_game_data(web_literals):
    time_before = time.time()

    game_scrapper = QueensScrapper(web_literals[GAME]['webpage_url'])
    game_scrapper.set_up_driver()
    board_data = {}
    try:
        game_scrapper.check_iframe()
        board_data['number'] = game_scrapper.get_board_number(web_literals['level_number_class'])
        game_scrapper.access_main_page(web_literals['play_button_ids'])
        board_data.update(
            game_scrapper.get_queens_board(web_literals[GAME]['board_div_id'], web_literals[GAME]['board_div_class']))
    finally:
        game_scrapper.close_web_driver()

    fetching_time = round(time.time() - time_before, 3)
    print(f'Board data fetched in {fetching_time}s')

    return board_data


def solve_board(game_data):
    solver = QueensSolver(game_data['board'], game_data['rows'])
    solution = []
    if solver.solve_puzzle():
        print(f"Queens Puzzle #{game_data['number']} solved in {solver.computing_time}s")
        solution = solver.get_model()
    else:
        print(f"Queens Puzzle #{game_data['number']} has no solution")

    return solution


web_literals = load_json(WEB_LITERALS)
styles = load_json(STYLES)
game_data = fetch_game_data(web_literals)
solution = solve_board(game_data)

if solution:
    visualizer = BoardPrinter(game_data['board'], game_data['rows'], solution, styles[GAME]['color_palette'])
    visualizer.solution_to_terminal()
    visualizer.solution_as_image(f"{SOLVED_BOARDS}/board_{game_data['number']}.png")
    game_data['solution'] = solution
    with open(f"{BOARD_INSTANCES}/instance_{game_data['number']}.json", 'w') as f:
        json.dump(game_data, f)
