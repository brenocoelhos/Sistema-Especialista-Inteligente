import unittest
from motor import carregar_base, ranking, plano

class MotorTests(unittest.TestCase):
    def setUp(self):
        self.base = carregar_base()
        self.respostas = {p['id']: 3 for p in self.base['perguntas']}

    def test_extremos(self):
        for valor, esperado in [(1, 0), (5, 100)]:
            for r in ranking(self.base, dict.fromkeys(self.respostas, valor)):
                self.assertAlmostEqual(r['compatibilidade'], esperado)

    def test_empate_neutro(self):
        r = ranking(self.base, self.respostas)
        self.assertEqual(len(r), 10)
        self.assertTrue(all(abs(t['compatibilidade'] - 50) < 1e-9 for t in r))

    def test_perfil_dados_web(self):
        self.respostas.update(matematica=5, dados=5, codigo=5, design=5)
        r = ranking(self.base, self.respostas)
        self.assertEqual(r, ranking(self.base, self.respostas))
        self.assertTrue(all(0 <= t['compatibilidade'] <= 100 for t in r))

    def test_penalidade_explicavel(self):
        self.respostas['logica'] = 1
        r = next(r for r in ranking(self.base, self.respostas) if r['id'] == 'backend')
        self.assertEqual(len(r['penalidades']), 1)
        self.assertAlmostEqual(r['compatibilidade'], max(0, r['bruto'] - 10))

    def test_entradas_invalidas(self):
        for valor in [0, 6, float('nan'), True, '3']:
            with self.assertRaises(ValueError):
                ranking(self.base, {**self.respostas, 'logica': valor})
        with self.assertRaises(ValueError):
            ranking(self.base, {})

    def test_gaps_e_tempo(self):
        vazio = plano(self.base, 'backend', {}, 5)
        self.assertEqual(len(vazio['gaps']), 5)
        self.assertLess(plano(self.base, 'backend', {}, 10)['semanas'], vazio['semanas'])
        completo = plano(self.base, 'backend', dict.fromkeys(self.base['competencias'], 2))
        self.assertEqual(completo['gaps'], [])
        with self.assertRaises(ValueError):
            plano(self.base, 'backend', {}, 0)

if __name__ == '__main__':
    unittest.main()
