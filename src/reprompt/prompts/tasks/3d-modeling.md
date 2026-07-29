## Task profile: 3d-modeling

Shape the rewritten prompt as a 3D asset production brief.

- Capture target engine or DCC tool (Blender, Maya, ZBrush, Unity, Unreal, glTF pipeline),
  intended use (real-time prop, hero character, cinematic, print, CAD/manufacturing), and
  final file format.
- Specify poly budget or triangle count range, topology requirements (quad-dominant,
  edge flow around deformation areas), and LOD count when the asset is real-time.
- Define UV layout expectations (single vs. multiple UDIMs, seam placement, overlap
  tolerance) and texel density target.
- Name the material pipeline (PBR metallic/roughness vs. specular/glossy), map set
  (albedo, normal, roughness, metallic, AO, emissive), resolution, and channel packing.
- For characters or props requiring animation, state rig type, bone count ceiling, weight
  painting constraints, and whether blend shapes are needed.
- State scale and unit convention (meters vs. centimeters), pivot placement, and
  world-origin alignment expected by the target engine.
- For CAD or manufacturing output, require exact real-world dimensions, tolerances, and
  wall-thickness or printability constraints instead of visual approximation.
- Acceptance should include polycount verification, clean topology check (no n-gons,
  no non-manifold geometry unless explicitly allowed), UV overlap check, and a render or
  in-engine import screenshot proving the asset loads correctly.
