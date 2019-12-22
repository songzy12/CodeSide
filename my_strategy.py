import model
import math

LOCAL = True


def distance_sqr(a, b):
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2


class MyStrategy:
    def __init__(self):
        pass

    def get_target_pos(self, unit, game, debug):
        self.target_pos = unit.position

        self.nearest_enemy = min(
            filter(lambda u: u.player_id != unit.player_id, game.units),
            key=lambda u: distance_sqr(u.position, unit.position),
            default=None)

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
            health_pack_positions = []
            for box in game.loot_boxes:
                if isinstance(box.item, model.Item.HealthPack):
                    health_pack_positions.append([distance_sqr(
                        box.position, unit.position), distance_sqr(box.position, self.nearest_enemy.position), box])
            health_pack_positions.sort()

            self.nearest_health_pack = None
            for unit_distance, enermy_distance, box in health_pack_positions:
                if unit_distance < enermy_distance:
                    self.nearest_health_pack = box
                    break
            if self.nearest_health_pack is None and health_pack_positions:
                self.nearest_health_pack = health_pack_positions[0][-1]

            debug.draw(model.CustomData.Log(
                "nearest_health_pack: {}".format(self.nearest_health_pack)))
            if self.nearest_health_pack is not None:
                self.target_pos = self.nearest_health_pack.position
                return

        if self.nearest_enemy is not None:
            # TODO: keep some distance
            self.target_pos = self.nearest_enemy.position
            return

    def get_velocity(self, unit, game, debug):
        # TODO: this may cause stuck
        self.velocity = self.target_pos.x - unit.position.x
        debug.draw(model.CustomData.Log(
            "velocity: {}\ttarget.x: {}\tunit.x: {}".format(self.velocity, self.target_pos.x, unit.position.x)))

        self.jump = self.target_pos.y > unit.position.y
        if self.target_pos.x > unit.position.x and \
                game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
            self.jump = True
        if self.target_pos.x < unit.position.x and \
                game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
            self.jump = True
        self.jump_down = not self.jump

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

    def get_shoot(self, unit, game, debug):
        self.reload = False

        # if there is a wall on the path from unit.position to enermy.position
        # then we will not let the unit shoot
        self.shoot = True
        x1, y1 = int(unit.position.x), int(unit.position.y)
        x2, y2 = int(self.nearest_enemy.position.x), int(
            self.nearest_enemy.position.y)
        if x2 < x1:
            x1, x2 = x2, x1
            y1, y2 = y2, y1

        if x1 == x2:
            return

        delta_y = (y2 - y1) // (x2 - x1)

        for t in range(x2 - x1):
            x = x1 + t
            y = y1 + delta_y * t
            if game.level.tiles[x][y] == model.Tile.WALL:
                self.shoot = False
                break

    def get_plant_mine(self):
        self.plant_mine = False

    def get_action(self, unit, game, debug):
        # Replace this code with your own

        self.get_target_pos(unit, game, debug)
        self.get_velocity(unit, game, debug)

        self.get_aim(unit)
        self.get_swap_weapon()
        self.get_shoot(unit, game, debug)
        self.get_plant_mine()

        return model.UnitAction(
            velocity=self.velocity,
            jump=self.jump,
            jump_down=self.jump_down,
            aim=self.aim,
            shoot=self.shoot,
            reload=self.reload,
            swap_weapon=self.swap_weapon,
            plant_mine=self.plant_mine)
