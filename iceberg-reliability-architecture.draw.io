<mxfile host="app.diagrams.net" modified="2026-08-24T04:49:00.000Z" agent="ChatGPT" version="24.7.17">
  <diagram id="icebergReliabilityArchitecture" name="Architecture">
    <mxGraphModel dx="1600" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1600" pageHeight="900" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <mxCell id="title" value="Beyond Row Counts — Apache Iceberg Reliability Lab" style="text;html=1;align=center;verticalAlign=middle;fontSize=28;fontStyle=1;whiteSpace=wrap;" vertex="1" parent="1">
          <mxGeometry x="260" y="30" width="1080" height="50" as="geometry"/>
        </mxCell>
        <mxCell id="subtitle" value="Watermark-based incremental processing + Iceberg metadata-driven reliability checks" style="text;html=1;align=center;verticalAlign=middle;fontSize=15;fontColor=#555555;whiteSpace=wrap;" vertex="1" parent="1">
          <mxGeometry x="320" y="82" width="960" height="30" as="geometry"/>
        </mxCell>

        <mxCell id="sourceZone" value="SOURCE SYSTEM" style="swimlane;html=1;rounded=1;horizontal=1;startSize=34;fontStyle=1;fontSize=14;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="60" y="160" width="300" height="420" as="geometry"/>
        </mxCell>
        <mxCell id="postgres" value="PostgreSQL&#xa;orders" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fontSize=16;fontStyle=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="sourceZone">
          <mxGeometry x="55" y="75" width="190" height="100" as="geometry"/>
        </mxCell>
        <mxCell id="generator" value="Deterministic Data Generator&#xa;seed = 42" style="rounded=1;whiteSpace=wrap;html=1;fontSize=14;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="sourceZone">
          <mxGeometry x="55" y="220" width="190" height="70" as="geometry"/>
        </mxCell>
        <mxCell id="watermark" value="Pipeline Watermark&#xa;(updated_at, order_id)" style="shape=note;whiteSpace=wrap;html=1;fontSize=13;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="sourceZone">
          <mxGeometry x="55" y="320" width="190" height="70" as="geometry"/>
        </mxCell>

        <mxCell id="pipelineZone" value="PIPELINE / PYICEBERG" style="swimlane;html=1;rounded=1;horizontal=1;startSize=34;fontStyle=1;fontSize=14;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="410" y="160" width="360" height="420" as="geometry"/>
        </mxCell>
        <mxCell id="extract" value="Incremental Extractor&#xa;watermark-based" style="rounded=1;whiteSpace=wrap;html=1;fontSize=15;fontStyle=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="pipelineZone">
          <mxGeometry x="65" y="70" width="230" height="70" as="geometry"/>
        </mxCell>
        <mxCell id="batch" value="Batch Artifact&#xa;Parquet + JSON metadata" style="shape=document;whiteSpace=wrap;html=1;fontSize=14;fillColor=#e1d5e7;strokeColor=#9673a6;" vertex="1" parent="pipelineZone">
          <mxGeometry x="65" y="175" width="230" height="70" as="geometry"/>
        </mxCell>
        <mxCell id="upsert" value="PyIceberg Upsert&#xa;join key: order_id" style="rounded=1;whiteSpace=wrap;html=1;fontSize=15;fontStyle=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="pipelineZone">
          <mxGeometry x="65" y="285" width="230" height="70" as="geometry"/>
        </mxCell>

        <mxCell id="icebergZone" value="ICEBERG TABLE LAYER" style="swimlane;html=1;rounded=1;horizontal=1;startSize=34;fontStyle=1;fontSize=14;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="820" y="160" width="380" height="420" as="geometry"/>
        </mxCell>
        <mxCell id="icebergTable" value="Apache Iceberg Table&#xa;reliability.orders" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fontSize=16;fontStyle=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="icebergZone">
          <mxGeometry x="85" y="65" width="210" height="95" as="geometry"/>
        </mxCell>
        <mxCell id="restCatalog" value="Iceberg REST Catalog&#xa;localhost:8181" style="rounded=1;whiteSpace=wrap;html=1;fontSize=14;fillColor=#ffe6cc;strokeColor=#d79b00;" vertex="1" parent="icebergZone">
          <mxGeometry x="35" y="210" width="145" height="70" as="geometry"/>
        </mxCell>
        <mxCell id="minio" value="MinIO&#xa;S3-compatible storage" style="shape=folder;whiteSpace=wrap;html=1;fontSize=14;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="icebergZone">
          <mxGeometry x="205" y="210" width="145" height="70" as="geometry"/>
        </mxCell>
        <mxCell id="snapshots" value="Snapshots + Data Files&#xa;record counts • null counts&#xa;lower/upper bounds • file stats" style="rounded=1;whiteSpace=wrap;html=1;fontSize=13;fillColor=#e1d5e7;strokeColor=#9673a6;" vertex="1" parent="icebergZone">
          <mxGeometry x="65" y="315" width="250" height="80" as="geometry"/>
        </mxCell>

        <mxCell id="reliabilityZone" value="RELIABILITY LAYER" style="swimlane;html=1;rounded=1;horizontal=1;startSize=34;fontStyle=1;fontSize=14;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="1250" y="160" width="300" height="420" as="geometry"/>
        </mxCell>
        <mxCell id="profile" value="Metadata Profile&#xa;aggregate file-level metrics" style="rounded=1;whiteSpace=wrap;html=1;fontSize=14;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="reliabilityZone">
          <mxGeometry x="45" y="65" width="210" height="70" as="geometry"/>
        </mxCell>
        <mxCell id="baseline" value="Baseline Comparison&#xa;healthy vs current snapshot" style="rounded=1;whiteSpace=wrap;html=1;fontSize=14;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="reliabilityZone">
          <mxGeometry x="45" y="165" width="210" height="70" as="geometry"/>
        </mxCell>
        <mxCell id="qualityGate" value="Metadata Quality Gate&#xa;PASS / FAIL" style="rounded=1;whiteSpace=wrap;html=1;fontSize=15;fontStyle=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="reliabilityZone">
          <mxGeometry x="45" y="265" width="210" height="75" as="geometry"/>
        </mxCell>
        <mxCell id="decision" value="Pipeline Reliability Decision" style="rounded=1;whiteSpace=wrap;html=1;fontSize=14;fontStyle=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="reliabilityZone">
          <mxGeometry x="45" y="365" width="210" height="50" as="geometry"/>
        </mxCell>

        <mxCell id="scenarioBand" value="RELIABILITY SCENARIOS" style="swimlane;html=1;rounded=1;horizontal=1;startSize=34;fontStyle=1;fontSize=14;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="160" y="640" width="1280" height="165" as="geometry"/>
        </mxCell>
        <mxCell id="corruptionScenario" value="Silent Corruption&#xa;10,000 → 10,000 rows&#xa;metadata detects drift" style="rounded=1;whiteSpace=wrap;html=1;fontSize=14;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="scenarioBand">
          <mxGeometry x="55" y="55" width="250" height="75" as="geometry"/>
        </mxCell>
        <mxCell id="incrementalScenario" value="Incremental Upsert&#xa;200 updates + 500 inserts&#xa;700-row change batch" style="rounded=1;whiteSpace=wrap;html=1;fontSize=14;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="scenarioBand">
          <mxGeometry x="355" y="55" width="250" height="75" as="geometry"/>
        </mxCell>
        <mxCell id="replayScenario" value="Crash + Replay&#xa;watermark not advanced&#xa;replay becomes no-op" style="rounded=1;whiteSpace=wrap;html=1;fontSize=14;fillColor=#e1d5e7;strokeColor=#9673a6;" vertex="1" parent="scenarioBand">
          <mxGeometry x="655" y="55" width="250" height="75" as="geometry"/>
        </mxCell>
        <mxCell id="lateScenario" value="Late Arrival&#xa;event-time cursor misses it&#xa;change-time cursor captures it" style="rounded=1;whiteSpace=wrap;html=1;fontSize=14;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="scenarioBand">
          <mxGeometry x="955" y="55" width="250" height="75" as="geometry"/>
        </mxCell>

        <mxCell id="e1" value="seed" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;" edge="1" parent="1" source="generator" target="postgres"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e2" value="read changes" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;" edge="1" parent="1" source="postgres" target="extract"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e3" value="cursor" style="edgeStyle=orthogonalEdgeStyle;rounded=0;dashed=1;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;" edge="1" parent="1" source="watermark" target="extract"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e4" value="persist batch" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;" edge="1" parent="1" source="extract" target="batch"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e5" value="apply" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;" edge="1" parent="1" source="batch" target="upsert"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e6" value="upsert" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;" edge="1" parent="1" source="upsert" target="icebergTable"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e7" value="catalog metadata" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;" edge="1" parent="1" source="icebergTable" target="restCatalog"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e8" value="data + metadata files" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;" edge="1" parent="1" source="icebergTable" target="minio"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e9" value="inspect" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;" edge="1" parent="1" source="icebergTable" target="snapshots"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e10" value="file metrics" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;" edge="1" parent="1" source="snapshots" target="profile"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e11" value="compare" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;" edge="1" parent="1" source="profile" target="baseline"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e12" value="evaluate rules" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;" edge="1" parent="1" source="baseline" target="qualityGate"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e13" value="result" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;" edge="1" parent="1" source="qualityGate" target="decision"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e14" value="advance only after successful apply + validation" style="edgeStyle=orthogonalEdgeStyle;rounded=0;dashed=1;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;fontSize=11;" edge="1" parent="1" source="decision" target="watermark"><mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="1390" y="610"/><mxPoint x="240" y="610"/></Array></mxGeometry></mxCell>

        <mxCell id="s1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;dashed=1;html=1;endArrow=open;endFill=0;strokeColor=#b85450;" edge="1" parent="1" source="corruptionScenario" target="qualityGate"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="s2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;dashed=1;html=1;endArrow=open;endFill=0;strokeColor=#82b366;" edge="1" parent="1" source="incrementalScenario" target="upsert"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="s3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;dashed=1;html=1;endArrow=open;endFill=0;strokeColor=#9673a6;" edge="1" parent="1" source="replayScenario" target="watermark"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="s4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;dashed=1;html=1;endArrow=open;endFill=0;strokeColor=#d6b656;" edge="1" parent="1" source="lateScenario" target="extract"><mxGeometry relative="1" as="geometry"/></mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
