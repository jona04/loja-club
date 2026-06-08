import { describe, expect, it } from "vitest"

import { buildMenu } from "./menu"

const titles = (permissions: string[]) =>
  buildMenu(permissions).map((module) => module.title)

describe("buildMenu", () => {
  it("always shows Dashboard, even with no permissions", () => {
    expect(titles([])).toEqual(["Dashboard"])
  })

  it("reveals Configurações with settings.view", () => {
    expect(titles(["settings.view"])).toContain("Configurações")
    expect(titles(["settings.view"])).not.toContain("Equipe")
  })

  it("reveals Equipe with team.view", () => {
    expect(titles(["team.view"])).toContain("Equipe")
  })

  it("shows every module for a full permission set", () => {
    expect(titles(["settings.view", "team.view"])).toEqual([
      "Dashboard",
      "Configurações",
      "Equipe",
    ])
  })
})
