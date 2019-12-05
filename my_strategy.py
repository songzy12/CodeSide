import model


def distance_sqr(a, b):
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2


class MyStrategy:
    def __init__(self):
        pass

    def get_target_pos(self, unit, game):
        self.nearest_enemy = min(
            filter(lambda u: u.player_id != unit.player_id, game.units),
            key=lambda u: distance_sqr(u.position, unit.position),
            default=None)
        self.nearest_weapon = min(
            filter(lambda box: isinstance(
                box.item, model.Item.Weapon), game.loot_boxes),
            key=lambda box: distance_sqr(box.position, unit.position),
            default=None)
        self.target_pos = unit.position
        if unit.weapon is None and self.nearest_weapon is not None:
            self.target_pos = self.nearest_weapon.position
        elif self.nearest_enemy is not None:
            self.target_pos = self.nearest_enemy.position

    def get_aim(self, unit):
        self.aim = model.Vec2Double(0, 0)
        if self.nearest_enemy is not None:
            self.aim = model.Vec2Double(
                self.nearest_enemy.position.x - unit.position.x,
                self.nearest_enemy.position.y - unit.position.y)

    def get_jump(self, unit, game):
        self.jump = self.target_pos.y > unit.position.y
        if self.target_pos.x > unit.position.x and \
                game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
            self.jump = True
        if self.target_pos.x < unit.position.x and \
                game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
            self.jump = True

    def get_action(self, unit, game, debug):
        # Replace this code with your own

        self.get_target_pos(unit, game)
        debug.draw(model.CustomData.Log(
            "Target pos: {}".format(self.target_pos)))

        self.get_aim(unit)
        self.get_jump(unit, game)

        return model.UnitAction(
            velocity=self.target_pos.x - unit.position.x,
            jump=self.jump,
            jump_down=not self.jump,
            aim=self.aim,
            shoot=True,
            reload=False,
            swap_weapon=False,
            plant_mine=False)
