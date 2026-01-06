  (function() {
    const raw = `year,female,male
  1900,23,913
  1901,34,399
  1902,7,521
  1903,6,305
  1904,3,230
  1905,12,464
  1906,5,306
  1907,8,341
  1908,3,590
  1909,1,246
  1910,14,625
  1911,3,591
  1912,80,663
  1913,62,748
  1914,56,612
  1915,22,547
  1916,38,507
  1917,20,340
  1918,24,377
  1919,27,641
  1920,49,1061
  1921,30,812
  1922,24,928
  1923,57,1065
  1924,27,823
  1925,45,1183
  1926,55,1377
  1927,66,1177
  1928,47,1379
  1929,190,731
  1930,188,1565
  1931,376,1010
  1932,55,708
  1933,103,850
  1934,237,870
  1935,83,718
  1936,107,659
  1937,198,660
  1938,223,622
  1939,76,595
  1940,105,691
  1941,64,896
  1942,132,646
  1943,22,783
  1944,40,717
  1945,42,905
  1946,139,890
  1947,89,1074
  1948,103,1181
  1949,67,937
  1950,81,1057
  1951,64,763
  1952,57,637
  1953,72,658
  1954,68,625
  1955,29,623
  1956,54,552
  1957,66,850
  1958,98,832
  1959,63,929
  1960,104,1108
  1961,73,1193
  1962,122,1473
  1963,222,1394
  1964,137,1688
  1965,268,1866
  1966,202,1953
  1967,282,1925
  1968,215,1808
  1969,126,1955
  1970,119,1691
  1971,93,1270
  1972,122,1331
  1973,312,1405
  1974,129,948
  1975,145,952
  1976,167,955
  1977,128,766
  1978,198,734
  1979,181,764
  1980,128,1051
  1981,123,725
  1982,142,745
  1983,143,827
  1984,204,753
  1985,133,587
  1986,85,646
  1987,163,645
  1988,140,808
  1989,223,698
  1990,306,598
  1991,124,957
  1992,183,631
  1993,252,333
  1994,313,604
  1995,463,384
  1996,248,425
  1997,244,453
  1998,269,703
  1999,559,433
  2000,302,552
  2001,379,778
  2002,460,721
  2003,414,917
  2004,441,606
  2005,255,521
  2006,267,388
  2007,317,351
  2008,195,579
  2009,222,304
  2010,114,248
  2011,142,321
  2012,126,272
  2013,92,299
  2014,45,140
  2015,44,87
  2016,6,24
  `;

    const margin = { top: 40, right: 20, bottom: 70, left: 60 };
    const baseWidth = 940;
    const height = 500 - margin.top - margin.bottom;

    const svgRoot = d3.select('#viz')
      .attr('width', baseWidth)
      .attr('height', height + margin.top + margin.bottom)
      .attr('viewBox', `0 0 ${baseWidth} ${height + margin.top + margin.bottom}`)
      .attr('preserveAspectRatio', 'xMidYMid meet');

    const svg = svgRoot.append('g').attr('transform', `translate(${margin.left}, ${margin.top})`);

    const data = d3.csvParse(raw)
      .map(d => {
        const year = +d.year;
        const femaleCount = +d.female || 0;
        const maleCount = +d.male || 0;
        const total = femaleCount + maleCount;
        const female = total ? (femaleCount / total) * 100 : 0;
        const male = total ? (maleCount / total) * 100 : 0;

        return {
          year,
          female,
          male,
          femaleCount,
          maleCount,
          total
        };
      })
      .sort((a, b) => a.year - b.year)
      .filter(d => d.year >= 1900 && d.year <= 2016);

    const keys = ['female', 'male'];
    const color = d3.scaleOrdinal().domain(keys).range(['#e45756', '#3b86c0']);

    const tooltip = d3.select('body')
      .append('div')
      .attr('id', 'moma-tooltip')
      .style('visibility', 'hidden')
      .style('position', 'absolute')
      .style('pointer-events', 'none')
      .style('background', 'rgba(0,0,0,0.85)')
      .style('color', '#fff')
      .style('padding', '6px 8px')
      .style('border-radius', '4px')
      .style('font-size', '12px')
      .style('z-index', '9999')
      .style('opacity', '0')
      .style('transition', 'opacity 120ms ease');

    const container = document.getElementById('d3-container');

    function render() {
      const containerWidth = Math.max(320, container.clientWidth || baseWidth);
      const innerWidth = containerWidth - margin.left - margin.right;

      svgRoot
        .attr('width', containerWidth)
        .attr('height', height + margin.top + margin.bottom)
        .attr('viewBox', `0 0 ${containerWidth} ${height + margin.top + margin.bottom}`);

      svg.selectAll('*').remove();

      const x = d3
        .scaleBand()
        .domain(data.map(d => d.year))
        .range([0, innerWidth])
        .padding(0.1);

      const y = d3.scaleLinear().domain([0, 100]).range([height, 0]);

      const stack = d3.stack().keys(keys);
      const series = stack(data);

      svg
        .append('g')
        .selectAll('g')
        .data(series)
        .join('g')
        .attr('fill', d => color(d.key))
        .selectAll('rect')
        .data(d => d.map(v => ({ key: d.key, year: v.data.year, y0: v[0], y1: v[1] })))
        .join('rect')
        .attr('x', d => x(d.year))
        .attr('y', d => y(d.y1))
        .attr('height', d => Math.max(0, y(d.y0) - y(d.y1)))
        .attr('width', x.bandwidth())
        .on('mouseover', (event, d) => {
          const dp = data.find(dd => dd.year === d.year) || {};
          const fPct = dp.female !== undefined ? dp.female.toFixed(1) : (d.key === 'female' ? (d.y1 - d.y0).toFixed(1) : '0.0');
          const mPct = dp.male !== undefined ? dp.male.toFixed(1) : (d.key === 'male' ? (d.y1 - d.y0).toFixed(1) : '0.0');
          const fCount = dp.femaleCount !== undefined ? dp.femaleCount : 0;
          const mCount = dp.maleCount !== undefined ? dp.maleCount : 0;

          tooltip
            .html(`${d.year}<br>Female: ${fPct}% (${fCount})<br>Male: ${mPct}% (${mCount})`)
            .style('visibility', 'visible')
            .style('opacity', '1');
        })
        .on('mousemove', event => {
          tooltip.style('left', event.pageX + 12 + 'px').style('top', event.pageY + 12 + 'px');
        })
        .on('mouseout', () => tooltip.style('opacity', '0').style('visibility', 'hidden'));

      svg
        .append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x).tickValues(x.domain().filter((_, i) => i % 5 === 0)))
        .selectAll('text')
        .attr('transform', 'rotate(-45)')
        .style('text-anchor', 'end');

      svg.append('g').call(d3.axisLeft(y).ticks(5).tickFormat(d => d + '%'));

      const legend = svg.append('g').attr('transform', `translate(${innerWidth - 180}, -30)`);

      keys.forEach((k, i) => {
        const g = legend.append('g').attr('transform', `translate(${i * 90}, 0)`);
        g.append('rect').attr('width', 12).attr('height', 12).attr('fill', color(k));
        g.append('text').attr('x', 16).attr('y', 10).text((k == "female") ? "Female" : "Male").style('font-size', '12px');
      });
    }

    // initial render
    render();

    // redraw on resize (debounced)
    let resizeTimer = null;

    window.addEventListener('resize', () => {
      if (resizeTimer) clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        render();
      }, 150);
    });
  })();