import model
import math

DELTA_X = 10


def distance_sqr(a, b):
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2


class MyStrategy:
    def __init__(self):
        pass

    def get_target_pos(self, unit, game, debug):
        self.target_pos = unit.position

        if unit.weapon is None:
            self.nearest_weapon = min(
                filter(lambda box: isinstance(
                    box.item, model.Item.Weapon), game.loot_boxes),
                key=lambda box: distance_sqr(box.position, unit.position),
                default=None)
            if self.nearest_weapon is not None:
                self.target_pos = self.nearest_weapon.position
                return

        if unit.health < game.properties.unit_max_health:
            self.nearest_health_pack = min(
                filter(lambda box: isinstance(
                    box.item, model.Item.HealthPack), game.loot_boxes),
                key=lambda box: distance_sqr(box.position, unit.position),
                default=None)

            debug.draw(model.CustomData.Log(
                "nearest_health_pack: {}".format(self.nearest_health_pack)))
            if self.nearest_health_pack is not None:
                self.target_pos = self.nearest_health_pack.position
                return

        self.nearest_enemy = min(
            filter(lambda u: u.player_id != unit.player_id, game.units),
            key=lambda u: distance_sqr(u.position, unit.position),
            default=None)
        if self.nearest_enemy is not None:
            # TODO: keep some distance
            self.target_pos = self.nearest_enemy.position
            return

    def get_velocity(self, unit, game, debug):
        # TODO: this may cause stuck
        self.velocity = self.target_pos.x - unit.position.x
        debug.draw(model.CustomData.Log(
            "Velocity: {}, target.x: {}, unit.x: {}".format(self.velocity, self.target_pos.x, unit.position.x)))

        self.jump = self.target_pos.y > unit.position.y
        if self.target_pos.x > unit.position.x and \
                game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
            self.jump = True
        if self.target_pos.x < unit.position.x and \
                game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
            self.jump = True

    def get_aim(self, unit):
        self.aim = model.Vec2Double(0, 0)
        if unit.weapon is not None and self.nearest_enemy is not None:
            self.aim = model.Vec2Double(
                self.nearest_enemy.position.x - unit.position.x,
                self.nearest_enemy.position.y - unit.position.y)
            aim_length = math.sqrt(self.aim.x ** 2 + self.aim.y ** 2)
            self.aim.x = 1 / aim_length * self.aim.x
            self.aim.y = 1 / aim_length * self.aim.y

    def get_swap_weapon(self):
        # TODO: implement this
        self.swap_weapon = False

    def get_shoot(self):
        # TODO: if explosion will hurt ourselves, then no shoot
        self.shoot = False
        self.reload = False

    def get_plant_mine(self):
        self.plant_mine = False

    def get_action(self, unit, game, debug):
        # Replace this code with your own

        self.get_target_pos(unit, game, debug)
        self.get_velocity(unit, game, debug)
        debug.draw(model.CustomData.Log(
            "Target pos: {}".format(self.target_pos)))

        self.get_aim(unit)
        self.get_swap_weapon()
        self.get_shoot()
        self.get_plant_mine()

        return model.UnitAction(
            velocity=self.velocity,
            jump=self.jump,
            jump_down=not self.jump,
            aim=self.aim,
            shoot=self.shoot,
            reload=self.reload,
            swap_weapon=self.swap_weapon,
            plant_mine=self.plant_mine)
