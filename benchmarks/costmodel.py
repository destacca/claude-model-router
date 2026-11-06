# Preços US$/MTok (platform.claude.com/docs/en/about-claude/pricing, 06/11/2026)
P = {  # (input, cache_write_5m, cache_read, output)
 'opus':   (4.0, 5.0, 0.20, 20.0),
 'sonnet': (2.0, 2.5, 0.10, 10.0),
 'haiku':  (0.10, 0.125, 0.01, 0.50),
}
F = 62.6e3   # piso medido de um subagente (tokens), neste ambiente
INC = 1.0e3  # incremento medido por chamada de ferramenta (~0.9-1.1k)

def main_direct(model, C, k, O, n, out_per_turn=300):
    _, pw, pr, po = P[model]; c = 0.0; ctx = C
    for i in range(k):                      # k turnos de ferramenta no principal
        c += ctx*pr/1e6 + O*pw/1e6 + out_per_turn*po/1e6
        ctx += O
    c += n*ctx*pr/1e6                       # n turnos restantes releem o acumulado
    return c

def main_delegate(model, sub, C, k, r, n, floor_cached, out_sub=300):
    _, pw, pr, po = P[model]
    c = C*pr/1e6 + r*pw/1e6 + 300*po/1e6    # 1 turno de spawn + resumo r
    c += n*(C+r)*pr/1e6
    _, spw, spr, spo = P[sub]; m = k+1      # subagente faz k chamadas + resposta final
    first = F*(spr if floor_cached else spw)/1e6
    rest = (m-1)*(F+INC*k/2)*spr/1e6
    c += first + rest + m*out_sub*spo/1e6
    return c

print(f"{'principal':8} {'sub':7} {'C':>5} {'k':>3} {'O':>5} | {'direto':>8} {'deleg(cache)':>12} {'deleg(frio)':>11} | economia(cache) economia(frio)")
rows=[]
for main in ['opus','sonnet']:
  for sub in ['haiku','sonnet']:
    if sub=='sonnet' and main=='sonnet': continue
    for C in [20e3,100e3]:
      for k,O in [(1,500),(4,1500),(10,3000)]:
        n=20
        d=main_direct(main,C,k,O,n)
        hc=main_delegate(main,sub,C,k,500,n,True)
        hf=main_delegate(main,sub,C,k,500,n,False)
        print(f"{main:8} {sub:7} {C/1e3:4.0f}k {k:3d} {O:5d} | {d:8.4f} {hc:12.4f} {hf:11.4f} | {100*(d-hc)/d:8.0f}% {100*(d-hf)/d:12.0f}%")
print()
# Implementação: 10 chamadas, principal Opus direto vs Opus->Sonnet sub vs principal Sonnet direto, saída 5k tokens
for C in [20e3,100e3]:
    k,O,n=10,3000,20
    opus=main_direct('opus',C,k,O,n)+5000*20/1e6
    son=main_direct('sonnet',C,k,O,n)+5000*10/1e6
    sub=main_delegate('opus','sonnet',C,k,800,n,False)+5000*10/1e6
    print(f"implementação C={C/1e3:.0f}k: Opus direto ${opus:.3f} | Opus orquestra+Sonnet sub ${sub:.3f} | tudo no Sonnet ${son:.3f}")
