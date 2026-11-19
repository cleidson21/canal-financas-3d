// Base comum das cenas de verificação das peças do EP001 (etapa 1 do Prompt 02).
// Monta terraço baixo + Nico (opções) + torre presa ao socket `costas`.
import { createTerracoBaixo } from '/biblioteca/cenarios/terraco_baixo.js';
import { createNico } from '/biblioteca/personagens/nico/index.js';
import { createTower } from '/biblioteca/objetos/torre_mercadorias.js';

export function montar(ctx, { descalco = true, sapatoQuebrado = false, quantidade = 6, altura = 1.0, comTorre = true } = {}) {
  const cen = createTerracoBaixo(ctx);
  const nico = createNico({ descalco, sapatoQuebrado });
  ctx.scene.add(nico.group);
  let torre = null;
  if (comTorre) {
    torre = createTower({ quantidade, altura });
    ctx.scene.add(torre);
  }
  // Encaixa a torre e atualiza o balanço (chamar a cada quadro, depois da pose).
  const prender = (t, amp = 1) => {
    if (!torre) return;
    nico.grab(torre, 'costas');
    torre.userData.update(t, amp);
  };
  return { cen, nico, torre, prender };
}
