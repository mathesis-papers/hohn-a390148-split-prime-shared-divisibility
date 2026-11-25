import argparse
from fractions import Fraction
import hashlib
import json
from itertools import permutations
from math import gcd, isqrt, lcm
from pathlib import Path


def factor(number):
    result = {}
    divisor = 2
    while divisor * divisor <= number:
        while number % divisor == 0:
            result[divisor] = result.get(divisor, 0) + 1
            number //= divisor
        divisor += 1
    if number > 1:
        result[number] = result.get(number, 0) + 1
    return result


def valuation(number, prime):
    exponent = 0
    while number % prime == 0:
        number //= prime
        exponent += 1
    return exponent


def check_quadruple(radii):
    assert len(radii) == 4 and all(radius > 0 for radius in radii)
    assert gcd(*radii) == 1
    common = lcm(*radii)
    curvatures = tuple(common // radius for radius in radii)
    assert gcd(*curvatures) == 1
    assert sum(curvatures) ** 2 == 3 * sum(value ** 2 for value in curvatures)
    assert all(curvature * radius == common for curvature, radius in zip(curvatures, radii))
    primes = sorted(factor(common))
    assert 3 in primes
    threshold_count = 0
    prime_count = 0
    witnesses = {}
    for prime in primes:
        orders = [valuation(radius, prime) for radius in radii]
        maximum = max(orders)
        assert min(orders) == 0
        assert orders.count(maximum) >= 2
        if prime == 3 or prime % 3 == 2:
            assert sorted(orders) == [0, maximum, maximum, maximum]
            if prime % 3 == 2:
                assert maximum % 2 == 0
        for exponent in range(1, maximum + 1):
            divisible = [index for index, order in enumerate(orders) if order >= exponent]
            assert len(divisible) in (2, 3)
            threshold_count += 1
            if prime % 3 == 1:
                witnesses.setdefault(str(len(divisible)), {
                    "radii": radii, "prime": prime, "exponent": exponent,
                    "coordinates": divisible,
                })
        prime_count += 1
    first, second, third, fourth = radii
    correction = Fraction(first * second * third,
                          gcd(first, second) * gcd(first, third) * gcd(second, third) * fourth)
    assert correction.denominator == 1
    for prime in factor(correction.numerator):
        assert prime % 3 == 1
        assert sum(radius % prime == 0 for radius in radii[:3]) >= 2
    return prime_count, threshold_count, witnesses


def enumerate_box(bound):
    solutions = set()
    triples = 0
    for first in range(1, bound + 1):
        for second in range(first, 3 * first + 1):
            for third in range(second, 4 * first + 1):
                triples += 1
                left, middle, right = second * third, first * third, first * second
                total = left + middle + right
                discriminant = 3 * (total * total - 2 * (left * left + middle * middle + right * right))
                if discriminant < 0:
                    continue
                square_root = isqrt(discriminant)
                if square_root * square_root != discriminant:
                    continue
                for denominator in {total - square_root, total + square_root}:
                    if denominator <= 0:
                        continue
                    numerator = 2 * first * second * third
                    fourth, remainder = divmod(numerator, denominator)
                    if remainder or fourth < third or gcd(first, second, third, fourth) != 1:
                        continue
                    solutions.add((first, second, third, fourth))
    return solutions, triples


def repeated_sphere_rows(parameter):
    rows = set()
    for first in range(1, parameter + 1):
        if parameter % first:
            continue
        second = parameter // first
        if gcd(first, second) != 1 or first % 3 == 0:
            continue
        for sign in [-1, 1]:
            curvature = first * first + 3 * second * second + sign * 3 * first * second
            row = tuple(sorted((3 * parameter * parameter, 3 * parameter * parameter,
                                3 * curvature * second * second, curvature * first * first)))
            check_quadruple(row)
            assert row not in rows
            rows.add(row)
    expected = 2 ** (len(factor(parameter)) - int(parameter % 3 == 0) + 1)
    assert len(rows) == expected
    return rows


def circle_row(first, second):
    assert first < second and gcd(first, second) == 1
    difference = second - first
    divisor = gcd(difference * difference, 4 * (first + second))
    values = (first * difference * difference, second * difference * difference,
              4 * first * second * (first + second), 4 * first * second * (first + second))
    assert all(value % divisor == 0 for value in values)
    row = tuple(value // divisor for value in values)
    assert gcd(*row) == 1
    reciprocals = [Fraction(1, value) for value in row]
    assert sum(reciprocals) ** 2 == 2 * sum(value * value for value in reciprocals)
    power = difference ** 3 // divisor
    cube = difference if difference % 2 else difference // 2
    coefficient = 2 if difference % 4 == 2 else 1
    assert power == coefficient * cube ** 3
    ordered = sorted(row)
    assert ordered[0] < ordered[1]
    assert (ordered[1] - 3 * ordered[0]) ** 2 <= 12 * ordered[0] ** 2 or ordered[1] <= 3 * ordered[0]
    first_reciprocal, second_reciprocal = [Fraction(1, value) for value in ordered[:2]]
    assert ordered[2] * (first_reciprocal - second_reciprocal) ** 2 <= 4 * (first_reciprocal + second_reciprocal)
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path(__file__).parent / "data" / "b390148.txt")
    parser.add_argument("--bound", type=int, default=60)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    assert 1 <= args.bound <= 100
    raw = args.data.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "50f1f6a5f9598aa3997b7fcd1f585a9576400aaffaaef2330505de5a1fd46b20"
    rows = []
    for line in raw.decode().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        index, value = map(int, line.split())
        assert index == len(rows) + 1
        rows.append(value)
    assert len(rows) % 4 == 0
    radii_rows = [tuple(rows[index:index + 4]) for index in range(0, len(rows), 4)]
    assert radii_rows == sorted(set(radii_rows))
    assert all(tuple(sorted(radii)) == radii for radii in radii_rows)
    prime_count = threshold_count = 0
    witnesses = {}
    for radii in radii_rows:
        primes, thresholds, found = check_quadruple(radii)
        prime_count += primes
        threshold_count += thresholds
        for key, value in found.items():
            witnesses.setdefault(key, value)
    generated, triples = enumerate_box(args.bound)
    expected = {radii for radii in radii_rows if radii[0] <= args.bound}
    assert generated == expected, {"extra": sorted(generated - expected), "missing": sorted(expected - generated)}
    for radii in generated:
        check_quadruple(radii)
    labelings = 0
    for radii in generated:
        for labeled in set(permutations(radii)):
            check_quadruple(labeled)
            labelings += 1
    norm_pairs = 0
    for prime in [2, 5, 11, 17, 23, 29]:
        for first in range(prime):
            for second in range(prime):
                assert ((first * first - first * second + second * second) % prime == 0) == (first == second == 0)
                norm_pairs += 1
    identity_cases = 0
    for first in range(8):
        for second in range(8):
            for third in range(8):
                for fourth in range(8):
                    difference_one, difference_two = third - second, fourth - second
                    norm = difference_one ** 2 - difference_one * difference_two + difference_two ** 2
                    quadratic = (first + second + third + fourth) ** 2 - 3 * sum(value ** 2 for value in [first, second, third, fourth])
                    assert quadratic == -2 * (2 * first ** 2 - first * (first + second + third + fourth) + norm)
                    identity_cases += 1
    repeated_count = 0
    repeated_examples = {}
    for parameter in range(1, 201):
        parameter_rows = repeated_sphere_rows(parameter)
        repeated_count += len(parameter_rows)
        if parameter <= 5:
            repeated_examples[str(parameter)] = sorted(parameter_rows)
    for radii in radii_rows:
        repeated = [value for value in set(radii) if radii.count(value) >= 2]
        if repeated:
            assert len(repeated) == 1 and repeated[0] % 3 == 0
            parameter = isqrt(repeated[0] // 3)
            assert 3 * parameter * parameter == repeated[0]
            assert radii in repeated_sphere_rows(parameter)
    circle_count = 0
    for second in range(2, 101):
        for first in range(1, second):
            if gcd(first, second) == 1:
                circle_row(first, second)
                circle_count += 1
    families_checked = 0
    for parameter in range(1, 101):
        first_family = circle_row(parameter, parameter + 1)
        repeated_radius = 4 * parameter * (parameter + 1) * (2 * parameter + 1)
        assert first_family == (parameter, parameter + 1, repeated_radius, repeated_radius)
        families_checked += 1
        if parameter % 2:
            second_family = circle_row(parameter, parameter + 2)
            repeated_radius = 2 * parameter * (parameter + 1) * (parameter + 2)
            corrected_index = (parameter + 1) // 2
            assert repeated_radius == 4 * corrected_index * (4 * corrected_index ** 2 - 1)
            assert second_family == (parameter, parameter + 2, repeated_radius, repeated_radius)
            families_checked += 1
        if parameter % 4 == 2:
            third_family = circle_row(parameter // 2, (parameter + 8) // 2)
            repeated_radius = parameter * (parameter + 4) * (parameter + 8) // 8
            source_index = (parameter - 2) // 4
            assert repeated_radius == (2 * source_index + 1) * (2 * source_index + 3) * (2 * source_index + 5)
            assert third_family == (parameter, parameter + 8, repeated_radius, repeated_radius)
            families_checked += 1
    erroneous_radii = (3, 5, 420, 420)
    reciprocals = [Fraction(1, radius) for radius in erroneous_radii]
    error_residual = sum(reciprocals) ** 2 - 2 * sum(value * value for value in reciprocals)
    assert error_residual == Fraction(-4, 315)
    membership = {}
    for target, unique in [(1, (1, 3, 3, 3)), (4, (3, 4, 12, 12)), (36, (28, 36, 63, 252))]:
        candidates = generated if args.bound >= target else enumerate_box(target)[0]
        matches = sorted(row for row in candidates if row[0] <= target and target in row)
        assert matches == [unique]
        membership[str(target)] = matches
    result = {
        "arithmetic": "exact integers and rational numbers",
        "data": {"source_url": "https://oeis.org/A390148/b390148.txt", "sha256": hashlib.sha256(raw).hexdigest(),
                 "terms": len(rows), "quadruples": len(radii_rows), "maximum_first_radius": max(row[0] for row in radii_rows)},
        "claims_checked": ["coefficient-three reciprocal equation", "common primitivity", "all-prime shared divisibility at every positive threshold",
                           "3-adic pattern (0,e,e,e)", "inert-prime pattern (0,2m,2m,2m), including 2", "split-prime support of gcd correction"],
        "prime_quadruple_pairs": prime_count,
        "positive_thresholds": threshold_count,
        "enumeration": {"first_radius": [1, args.bound], "second_radius": "first..3*first", "third_radius": "second..4*first",
                        "fourth_radius": "both exact quadratic roots, retaining positive integral fourth>=third",
                        "triples": triples, "solutions": len(generated), "agrees_with_data": True,
                        "scope": "The proved radius bounds make this enumeration exhaustive for first radius at most the stated bound; no assertion for larger first radii.",
                        "distinct_labelings_checked": labelings},
        "inert_norm": {"primes": [2, 5, 11, 17, 23, 29], "residue_pairs": norm_pairs},
        "polynomial_identity": {"curvature_coordinates": [0, 7], "tuples": identity_cases},
        "repeated_spheres": {"parameter_range": [1, 200], "quadruples": repeated_count,
                             "all_table_repetitions_classified": True, "examples": repeated_examples},
        "repeated_circles": {"coprime_parameter_range": "1<=u<v<=100", "quadruples": circle_count,
                             "three_family_examples": families_checked,
                             "second_family_correction": {"source_index": "k", "corrected_index": "(k+1)/2",
                                                          "source_example": erroneous_radii,
                                                          "equation_residual": str(error_residual),
                                                          "corrected_example": [3, 5, 120, 120]}},
        "exhaustive_containing_rows": membership,
        "split_prime_threshold_witnesses": witnesses,
        "scope": "Finite checks of the stated examples and ranges; the unbounded results have written proofs in note.pdf.",
        "all_assertions_passed": True,
    }
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
